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

        bracket = (bracket.cut(sidehole)
                        .faces(">Z")
                        .workplane()
                    )

    # Now build the half above the plug.
    bracket = (bracket.box(dt.size, dt.size, db.bthick, centered=(1,1,0))
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
                    # Having it excessively tight makes the part weaker though. Eh.
                    .edges("|Y and <Z").fillet(offs/4)
                )


    # Then I'll select the target edge to round off via some convoluted method.
    # I have no fucking clue why selector indexing refuses to pick it out.
    # And of course, a 100% fillet fails, so we got to settle for 99.9%.

    # And of fucking course x2, with this edge selection method, we got to use
    # a different set of selectors depeneding on whether we're building this
    # with the press-fit plug or not. Blarg.
    if dbp.use:
        bracket = (bracket.edges("|X")
                    .edges("not(>Y or <Y)")
                    .edges("not(>Z or <Z)")
                    .edges(">Z")
                  )
    else:
        bracket = (bracket.edges("|X")
                    .edges("not(>Y or <Y)")
                    .edges("<Z")
                  )

    bracket = bracket.fillet(min(0.999, db.reinforce) * (dt.size - db.sthick))

    # Then I'll cut the negative space out.
    bracket = bracket.cut(filletcutter)
    bracket = bracket.cut(veecutter)

    # And lastly, a pilot hole through the center vertical, as planned.
    bracket = bracket.faces("<Z").workplane().circle(db.pilot/2).cutThruAll()

    return bracket


def build_slider(dims):
    ds = dims.slider
    dt = dims.tube

    outside = dt.size + 2*ds.thickness
    inside = dt.size + ds.slack
    nut = cs.geometry.circumscribe(wrench=ds.nut.width)

    slider = (cq.Workplane("XY")
                .rect(outside, outside)
                .extrude(outside)
                .edges("|Z")
                .fillet(dims.bracket.plug.fillet)
                .faces(">Z")
                .workplane()
                .rect(inside, inside)
                .cutThruAll()
             )

    # Holder for the rub indicator.
    cross = (slider.faces("<X")
                .workplane()
                .box(outside/2, ds.pilot*2.5, ds.pilot*2.5 ,centered=(1,1,0), combine=0)
                .faces(">Y")
                .workplane()
            )

    # If using the nut instead of a tap... make the relief for the nut, but don't cut it
    # until later, because otherwise fillets and edge selection will be a bitch and a half.
    if not ds.tap:
        ds.pilot = ds.clearance
        tapnut = cross.polygon(6, nut).extrude(-ds.nut.depth, combine=False)

    cross = (cross
                .hole(ds.pilot)
                .edges("<X and |Y")
                .fillet(ds.pilot)
            )

    points = [(-outside/4,0),(outside/4,0)]
    slider = (slider.faces("<Y")
                .workplane()
                .transformed((0,90,0))
                .pushPoints(points)
                .circle(nut/2)
                .extrude(ds.nut.depth/3)
                .faces("<Y[3]")
                .edges()
                .fillet(min(ds.nut.depth/3*0.99, (outside/2-nut)/4*0.99))
              )

    slider = (slider.faces("<Y[2]")
                .workplane()
                .transformed((0,90,0))
                .pushPoints(points)
                .polygon(6, nut)
                .cutBlind(-ds.nut.depth)
              )

    slider = (slider.faces("<Y")
                .workplane()
                .transformed((0,90,0))
                .pushPoints(points)
                .hole(ds.clearance, ds.thickness*2)
              )

    slider=slider.union(cross)
    slider=slider.faces(">Z[-3]").edges("|Y").fillet(ds.pilot)
    slider=slider.faces("<Z[-3]").edges("|Y").fillet(ds.pilot)

    # Finally time to cut the holder for this nut. Retain with super glue, duh.
    if not ds.tap:
        slider = slider.cut(tapnut)

    return slider



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

    names = ['bracket', 'indicator', 'slider']
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
        FreeCAD.newDocument(obj.val().label)
        cs.pretty(obj) # But would be nice to see one.
