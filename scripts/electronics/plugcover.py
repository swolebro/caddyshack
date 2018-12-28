"""A simple cover for keeping plug prongs from getting bent up while not in use."""

import cadquery as cq
import caddyshack as cs

def build(dims):
    # Dividing these parts up so we can select things separately and fillet...
    # Selectors make it easy to select lots of things, but sometimes harder
    # if you don't want to select *all the things.*

    block = cq.Workplane("XY").box(dims.width, dims.depth, dims.height)
    filleted = copy(block).edges("<Z or |Z").fillet(dims.fillets.edges)

    prongs = (block
                .faces(">Z")
                .workplane()
                .pushPoints([(-dims.prongs.spacing/2,0),(dims.prongs.spacing/2,0)])
                .rect(dims.prongs.thickness, dims.prongs.width)
                .extrude(-dims.prongs.length, combine=False)
                )

    block = (block.cut(prongs).edges("|Y").fillet(dims.fillets.prongs))
    return block.intersect(filleted)

def copy(obj):
    # A gross hack.
    return obj.translate((0, 0, 0))

cs.clear()
dims = cs.Dims('scripts/electronics/plugcover.yml')
obj = build(dims)
cs.showsave(obj, dims)
