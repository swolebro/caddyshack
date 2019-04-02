"""A set of clips to hold up the gym mirror."""

import cadquery as cq
import caddyshack as cs

dims = cs.Dims('scripts/gym/mirror-clips.yml')
clip = dims.clip

# Add an extra 1/2 standoff for the cap on top.
clip.height = clip.standoff * 1.5 + dims.mirror
clip.depth = dims.screw.head * 2 + clip.overhang

part = (cq.Workplane("XY")
            .box(clip.width, clip.depth, clip.height)
            .edges("|Z")
            .fillet(3*clip.fillet)
            )

part = (part.faces(">Y").workplane(invert=True)
            .move(0, -clip.height/2 + dims.mirror/2 + clip.standoff/2)
            .rect(clip.width, dims.mirror)
            .cutBlind(clip.overhang)
            )

part = (part.faces(">Z").workplane()
            .move(0, -1/2*clip.depth + dims.screw.head)
            .cskHole(dims.screw.clearance, dims.screw.head, 82)
            )

# Should technically be able to do scew_head/2, but the cskHole oversinks
# by a good bit it seems.
part = part.edges(">Z").fillet(min(clip.fillet, dims.screw.head/3))

# Fin.
cs.showsave(part, dims=dims)
