"""Builds a puck that can house an array of magnets to use as a
rotary demagnetizing tool.

As in: https://www.youtube.com/watch?v=10enFh_OXZg
"""

import cadquery as cq
import caddyshack as cs


cs.clear()

dims = cs.Dims("scripts/shop/magnets/demag-tool.yml")

# Apply the fudge factors.
dims.bolt.wrench = dims.bolt.wrench * (1+dims.bolt.fudge)
dims.mag.size = dims.mag.size + dims.mag.fudge

# Build the puck with the bolt hole.
part = (cq.Workplane("XY")
            .circle(dims.dia/2)
            .extrude(dims.base)
            .edges()
            .fillet(dims.fillet)
            .faces(">Z")
            .workplane()
            .polygon(6, cs.geometry.circumscribe(n=6, wrench=dims.bolt.wrench))
            .cutBlind(-dims.bolt.cap)
            .faces("<Z")
            .workplane()
            .hole(dims.bolt.pilot)
        )

# Make each slot for the array, then cut them out.
slots = []
for i in range(dims.array.N):
    # Move the workplane to the appropriate spot.
    # Not using a polygon with .vertices() because we need the rotation too.
    slot = (part
            .faces(">Z")
            .workplane()
            .transformed((0,0,360/dims.array.N * i))
            .transformed((0,0,0), (dims.array.dia/2,0,0))
           )

    if dims.mag.kind == "round":
        slot = slot.circle(dims.mag.size/2)
    elif dims.mag.kind == "square":
        slot = slot.rect(dims.mag.size, dims.mag.size)
    else:
        raise Exception('mag.kind must be "round" or "square"')

    slot = slot.extrude(-dims.mag.depth, combine=False)
    slots.append(slot)

for slot in slots:
    part = part.cut(slot)

cs.showsave(part, dims=dims)
