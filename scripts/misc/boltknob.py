"""This script builds hand knobs for hex cap bolts.

This was designed and tested with 1/2" bolts and 6-point knobs,
and only lightly tested on a few smaller ones. I wouldn't be
surprised if a few edits could break the script or crash FreeCAD.

More bolt types and knob types to come.
"""

import urllib

import cadquery as cq
import caddyshack as cs


def build_knob(dims, bolt):
    dk = dims.knob

    width = dk.size.width * bolt.wrench
    height = max(dk.limits.height, dk.size.height*bolt.cap)
    support = min(dk.limits.support, dk.size.support*bolt.cap)
    rover = min(dk.limits.roundover, dk.size.roundover*bolt.cap)

    # Radius of circle that circumscribes this knob.
    radius = cs.geometry.circumscribe(n=dk.points, apo=width/2)

    # TODO: Fix the hex-only bolt assumption.
    bradius = cs.geometry.circumscribe(n=6, apo=bolt.wrench/2) * (1+bolt.fudge)
    hole = bolt.dia * (1+bolt.fudge)

    # Start with the bare polygon.
    knob = (cq.Workplane("XY")
                .polygon(dk.points, radius)
                .extrude(height)
                )

    # Make a cutout at each vertex, preserving the flats between them.
    knob = (knob.vertices()
                .hole(2*radius/dk.points)
            )
    # Fillet edges.
    knob = knob.edges("|Z").fillet(radius / (2*dk.points) * dk.size.roundoff)
    knob = knob.faces(">Z").fillet(rover)

    # Make the hex bolt hole.
    knob = (knob.faces(">Z")
                .workplane()
                .polygon(6, bradius)
                .cutBlind(-height + support)
                .faces("<Z")
                .workplane()
                .hole(hole)
                )

    return knob

if __name__ == "__cq_freecad_module__":
    cs.clear()

    dims = cs.Dims('scripts/misc/boltknob.yml')

    for name, bolt in dims.bolts.items():
        obj = build_knob(dims, bolt)
        obj.val().label = "n%d-%s" % (dims.knob.points, urllib.parse.quote(name, safe=""))
        cs.showsave(obj, dims)
