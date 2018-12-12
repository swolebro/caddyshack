"""Standoffs for screwing PCB's in place on the workbench for prototyping."""

import urllib

import FreeCAD

import cadquery as cq
import caddyshack as cs

def build_standoff(toe, height, boardcut, hbuffer, holesize, countersunk):

    # Figure out wtf we're doing with these args.

    # Add height to compensate for any notch cut for the board.
    if boardcut:
        height += boardcut

    # Hack for doing the right kind of hole.
    if countersunk:
        holefunc = "cskHole"
        holeargs = (holesize, countersunk, 82)
    else:
        holefunc = "hole"
        holeargs = (holesize,)

    # Make the part that retains the board.
    standoff = cq.Workplane("XY").box(toe*2, toe*2, height)

    if boardcut:
        standoff = standoff.faces(">Z").rect(toe, toe, centered=False).cutBlind(-boardcut)

    # Now make the part that will hold the screw, offset enough that
    # it won't interfere with the corner of the PCB.
    holepart = (cq.Workplane("XY", origin=(-hbuffer/2, -hbuffer/2, 0))
                    .box(hbuffer, hbuffer, height)
                )

    # Since we want to cut a hole in the center of the holepart, but
    # following that with a union would swallow the hole... we start
    # by cutting it all out, then cutting the hole, then putting it back.
    # lolwhut
    standoff = standoff.cut(holepart)
    holepart = getattr((holepart.faces(">Z")
                    .workplane()
                ), holefunc)(*holeargs)  # This is where I kinda wish hole() alone
                                         # had copious kwargs.

    standoff = standoff.union(holepart)
    return standoff

if __name__ == "__cq_freecad_module__":
    cs.clear()

    dims = cs.Dims('scripts/electronics/standoff.yml')
    ds = dims.standoff
    dw = dims.wireclamp

    # Calculate buffer for the holes.
    if dims.countersunk:
        hbuffer = (dims.countersunk)*1.1
    else:
        hbuffer = (dims.pilot)*1.75

    for tname, toe in ds.toe.items():
        for hname, height in ds.heights.items():
            # First build the bottom part:
            standoff = build_standoff(toe, height, ds.thick, hbuffer, dims.clearance, None)
            standoff.val().label = "%s-%s" % (tname, hname)
            cs.showsave(standoff, dims)

            # Close it so we don't spam too many.
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.ActiveObject.Label)

        # Just show the last one.
        FreeCAD.newDocument(standoff.val().label)
        cs.pretty(standoff)

        # Then build a cap that finishes the retaining. These don't vary with height of the standoff.
        cap = build_standoff(toe, dims.countersunk*0.25, None, hbuffer, dims.clearance, dims.countersunk)
        cap.val().label = "cap-%s" % (tname)
        cs.showsave(cap, dims)
