"""Builds a tool for adjusting Mavic UST rim splined nipples and for holding
bladed spokes.
"""

import cadquery as cq
import caddyshack as cs

cs.clear()
dims = cs.Dims("scripts/bikes/mavic-spline.yml")

# This part is basically yanked from my boltknob script.
radius = cs.geometry.circumscribe(n=dims.knob.N, apo=dims.knob.size/2)

knob = (cq.Workplane("XY")
              .polygon(dims.knob.N, radius)
              .extrude(dims.knob.base)
              .vertices()
              .hole(2*radius/dims.knob.N)
			.edges("|Z")
			.fillet(radius  / (2*dims.knob.N) * 0.99)
			.faces("#Z")
			.fillet(dims.knob.fillet)
              .faces(">Z")
              .workplane()
              .circle(radius=dims.nipple.dia*1.5)  # Make significantly larger than the nipple itself.
		    .extrude(dims.knob.stickout)
            )

# Slit for sliding along a bladed spoke.
slit = (cq.Workplane("XZ")
           .move(0, (dims.knob.base+dims.knob.stickout)/2)
    	      .rect(dims.spoke.thick, dims.knob.base + dims.knob.stickout)
           .extrude(dims.knob.size)
            )

# Bladed spoke holder.
blade = (cs.copy(knob).cut(slit))


# A different slit that can move past the round part of the spoke and over the nipple
slit = (cq.Workplane("XZ")
           .move(0, (dims.knob.base+dims.knob.stickout)/2)
    	      .rect(dims.spoke.dia, dims.knob.base + dims.knob.stickout)
           .extrude(dims.knob.size)
            )

# Block for the wrench. Similar to the blade tool, but sized for the round part of the spoke,
# and with a hole so it centers well.
wrench = (cs.copy(knob).faces(">Z").workplane().hole(dims.spoke.dia*1.33).cut(slit))

# Modeling a nipple to cut from the wrench.
nipple  = (cq.Workplane("XY")
                .workplane(offset=dims.knob.base+dims.knob.stickout-dims.nipple.height)
                .circle(dims.nipple.dia/2)
                .extrude(dims.nipple.height)
            )

# Basically steadling this from my Halbach demag tool script.
slots = []
for i in range(dims.nipple.spline.N):
    slot = (nipple
               .faces(">Z")
               .workplane()
               .transformed((0,0,360/dims.nipple.spline.N * (i+0.5))) # The 0.5 turns it out half a notch relative to the slit.
              )

    if dims.nipple.spline.kind == "vee":
        dist = dims.nipple.dia/2 + dims.nipple.spline.size/2*(2**0.5) - dims.nipple.dia/2 * dims.nipple.spline.depth
        slot = (slot.transformed((0,0,45),(dist,0,0)).rect(dims.nipple.spline.size, dims.nipple.spline.size))
    else:
        raise Exception('only supporing type "vee" right now, not %s' % dims.nipple.spline.kind)

    slot = slot.extrude(-dims.nipple.height, combine=False)
    slots.append(slot)

for slot in slots:
    nipple = nipple.cut(slot)

wrench = wrench.cut(nipple)

wrench.val().label = "wrench"
blade.val().label = "blade"

cs.showsave(wrench, dims)
cs.showsave(blade, dims)