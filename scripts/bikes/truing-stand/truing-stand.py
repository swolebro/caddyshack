"""CAD script to make a bicycle wheel truing stand.

See the README and the dimensions.yml file for informatoin on how to
run this script, then print and assemble it.
"""

import itertools
import os

import cadquery as cq
import caddyshack as cs

cs.clear()

# This is full of repetitive shitcode. It's dangerously close to the
# idiotmatic "String myString = new String("string") //This is my string"
# type stuff. TODO.

def build_bracket(dims):
    dt = dims.tube
    db = dims.bracket
    dbp = dims.bracket.plug

    bracket = cq.Workplane("XY")

    if dbp.use:
        # Build the insert plug.
        bot, mid, top = [dt.inside * dbp[x] for x in ['bot','mid','top']]
        bracket = (bracket.rect(bot, bot)
                    .workplane(offset=dbp.height*dbp.midheight)
                    .rect(mid,mid)
                    .loft()
                    .faces(">Z").rect(mid,mid)
                    .workplane(offset=dbp.height*(1-dbp.midheight))
                    .rect(top, top)
                    .loft()
                    .edges("(not |X) and (not |Y)")
                    .fillet(dbp.fillet)

                    # This extra fillet compensates for any smushing of the
                    # first few layers against the print bed.
                    .edges("<Z")
                    .fillet(dbp.height*dbp.midheight*0.2)
                  )

        # Seems like the easiest way to knock a hole through the side of a
        # loft is to extrude a cylinder in place and cut it out.
        # Cant't readily identify any reference planes for it.
        sidehole = (cq.Workplane("XZ")
                        .move(0.0, dbp.height/2)
                        .workplane(offset=-top/2)
                        .circle(db.pilot/2)
                        .extrude(top)
                    )

        bracket = bracket.cut(sidehole)

    # Now build the half above the plug.
    bracket = (bracket.faces(">Z")
                .workplane()
                .box(dt.size, dt.size, db.bthick, centered=(1,1,0))
                .faces(">Z")
                .workplane()
                .move(0, dt.size/2-db.sthick)
                .box(dt.size, db.sthick, dt.size, centered=(1,0,0))
              )

    # This shit is broken right to hell.
    # I want to reinforce junction between the two faces of the bracket,
    # though I want the center part to remain clear to allow room for a
    # skewer nut or quick release. I've also got to cut out a V shape for
    # that skewer to sit in.

    # First, I'll make the negative shape for cutting out the reinforcement.
    filletcutter = (bracket.faces(">Z[-2]")
                        .workplane()
                        .move(0,0)
                        .rect(dt.size - db.reinforce_thick*2, dt.size-db.sthick)
                        .extrude(dt.size, combine=False)
    )

    # Then one for the V.
    # The alignment here was kind of a proportional guess-and-check for what looked good.
    offs = dt.size/2
    veecutter = (bracket.faces(">Y")
                    .workplane()

                    # Turn so triangle points down. Move up for alignment.
                    .transformed((0,-90,0), (0,offs,0.0))
                    .polygon(3, offs*(8**0.5))
                    .extrude(-db.sthick, combine=False)

                    # The hub is what sits inside the V, not the skewer, so the fillet here
                    # not a critical dimension, so long as it is tighter than a bike dropout.
                    .edges("|Y and <Z").fillet(offs/8)
                )


    # Then I'll select the target edge to round off via some convoluted method.
    # I have no fucking clue why selector indexing refuses to pick it out.
    # And of course, a 100% fillet fails, so we got to settle for 99.9%.
    bracket = (bracket.edges("|X")
                .edges("not(>Y or <Y)")
                .edges("not(>Z or <Z)")
                .edges(">Z")
                .fillet(min(0.999, db.reinforce) * (dt.size - db.sthick))
               )

    # Then I'll cut the negative space out.
    bracket = bracket.cut(filletcutter)
    bracket = bracket.cut(veecutter)

    # And lastly, a pilot hole through the center vertical, as planned.
    bracket = bracket.faces("<Z").workplane().circle(db.pilot/2).cutThruAll()

    return bracket


def build_slider(dims):
    pass

def build_indicator(dims):
    x = dims.indicator
    x.rad = x.dia/2
    indicator = (cq.Workplane("XY")
                    .circle(x.rad)
                    .extrude(x.length - x.rad)
                    .faces(">Z")
                    .workplane()
                    .sphere(x.rad)
                    .faces("<Z")
                    .workplane()
                    .hole(dims.slider.pilot, x.length - x.rad)
                )

    return indicator


def build_spacer(dims, width):
    d = dims.spacer
    spacer = (cq.Workplane("XY")
                .rect(dims.tube.size, d.oncenter*2)
                .extrude(width)
                .faces(">Z")
                .workplane()
                .pushPoints([(0,d.oncenter/2), (0,-d.oncenter/2)])
                .hole(d.pilot)
                .edges("|Z")
                .fillet(d.pilot)
                .edges("not(|Z)")
                .fillet(d.fillet)
               )
    return spacer

# Do I even want to test for this? Will require refactoring later
# when I get this stuff running outside of FreeCAD. TODO.
if __name__ == "__cq_freecad_module__":
    dims = cs.Dims('scripts/bikes/truing-stand/dimensions.yml')

    names = ['bracket', 'indicator']
    for name in names:
        obj = globals()["build_" + name](dims) # oh god
        obj.val().label = name
        cs.showsave(obj, dims)

    # This is one example of where the list->dict conversion rears its head. Blarg.
    for width in dims.spacer.widths.values():
        obj = build_spacer(dims, width)
        obj.val().label = "spacer-%d" % width
        doc = cs.showsave(obj, dims)

        # Hack. Because we don't need to see *all* the spacers.
        import FreeCAD
        FreeCAD.closeDocument(FreeCAD.ActiveDocument.ActiveObject.Label)
    else:
        cs.pretty(obj) # But would be nice to see one.
