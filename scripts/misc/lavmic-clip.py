"""A plastic lav mic clip that can be affixed a shirt via a magnet.

Glue a small steel collar stay (or other steel shim, eg. a small washer) on the
back of the clip, then put a neodymium magnet or two on the inside of your
shirt, sweatjacket, etc. It's especially nice that you can place it a few
inches down from the collar, so it picks up less noise from you.

I haven't personally noticed any distortion on the signal line from the
magnets, and there shouldn't be any, given that there won't be any relative
motion between the wire and the magnets. Audiophiles claiming othewise can
shove it.
"""

import cadquery as cq
import caddyshack as cs

import math

def build(dims):

    base = (cq.Workplane("XY")
               .rect(dims.base.width, dims.base.length)
               .extrude(dims.base.fillet)
               .edges("|Z")
               .fillet(dims.base.fillet)
           )

    # This countersink will be half the length of the hole and
    # grow from the hole size to hole*(1+taper). So here's some trig.
    angle = math.degrees(math.atan(2*(dims.lav.hole*dims.lav.taper)/(dims.lav.length)))

    lav = (base.faces(">Z")
               .workplane()
               .move(0, dims.base.length*dims.lav.position)
               .rect(dims.lav.width, dims.lav.length)
               .extrude(dims.lav.height, combine=False)
               .edges("|Y and >Z")
               .fillet(dims.lav.fillet)
               .faces(">Y").workplane()

               # Move so that 1/3 of the hole is dropped, so you get a semi-springy
               # clip thing that doesn't just drop the mic (or walk away).
               .transformed(offset=(0,dims.lav.height/2 - dims.lav.hole*0.33,0))
               .cskHole(dims.lav.hole, dims.lav.hole*(1+dims.lav.taper), angle)
          )

    wire = (base.faces(">Z")
               .workplane()
               .move(0,-dims.base.length*dims.wire.position)
               .rect(dims.wire.width, dims.wire.length)
               .extrude(dims.wire.height, combine=False)
               .edges("|Y and >Z")
               .fillet(dims.wire.fillet)
               .faces(">Z")
               .workplane()
               .rect(dims.wire.slot.width, dims.wire.length)
               .cutBlind(-dims.wire.slot.depth)
           )

    return base.union(lav).union(wire)

if __name__ == "__cq_freecad_module__":
    cs.clear()

    dims = cs.Dims('scripts/misc/lavmic-clip.yml')
    obj = build(dims)
    cs.showsave(obj, dims)
