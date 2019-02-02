"""A simple set of boxes for building a Halbach array demo.

As shown in: https://www.youtube.com/watch?v=10enFh_OXZgd

Note that the magnets should be inserted such that the field
points along the border and separator lines, not along the
open faces of the fixture.
"""

import cadquery as cq
import caddyshack as cs


dims = cs.Dims(
"""
output:
    basename: linear-halbach
    baseunit: mm

border: 0.125 in  # thickness for the 4 perimeter walls
sep: 0.0625 in    # thickness for the seperators between magnets

N: 9              # number of magnets
mag: 10.4 mm      # slip-fit for 10mm cube magnet

fillet: 0.02 in   # taking the edge off
""")


cs.clear()

# Calculate the overall size.
L = dims.mag*dims.N + (dims.N-1)*dims.sep + 2*dims.border
W = dims.mag+2*dims.border

# Make the main body of the fixture.
part = cq.Workplane("XY").box(L, W, dims.mag, centered=(False, True, False))

# Now create a slot for each magnet.
blocks = []
for i in range(dims.N):
    block = (cq.Workplane("XY")
                .move(dims.border + dims.mag/2 + i*(dims.mag+dims.sep), 0)
                .rect(dims.mag, dims.mag)
                .extrude(dims.mag)
            )
    blocks.append(block)

for block in blocks:
    part.cut(block)

part.edges().fillet(dims.fillet)

cs.showsave(part, dims=dims)
