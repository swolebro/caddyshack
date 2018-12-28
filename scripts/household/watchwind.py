"""This makes a little tray you can ziptie a watch to, attach to a stepper,
and have that stepper move back and forth to recharge mechanical or
electromechanical (eg. Seiko Kinetic) watch."""

import cadquery as cq
import caddyshack as cs
import numpy as np

def build(dims):

    # Start with the part that backs the watch strap.
    result = (cq.Workplane("XY").box(dims.holder.length, dims.holder.width, dims.thick)

                # Add a spine that will have holes for zip ties.
                .faces(">Z")
                .workplane()
                .box(dims.holder.length, dims.thick, dims.thick, centered=(1,1,0))
                .edges()
                .fillet(dims.thick*0.15)

                # Working upwards, add the mount for the motor shaft.
                # The workplane offset is a silly trick to make the mount cylinder
                # blend through the fillet we added in the last step.
                # You don't want to add the fillet at the very end if you don't
                # have to, otherwise it's damn near impossible to avoid selecting
                # edges that throw BRep errors from fillets hitting other geometries...
                .faces(">Z[-2]")
                .workplane(offset=-dims.thick/2)
                .circle(dims.mount.dia/2 + dims.thick)
                .extrude(dims.mount.length + dims.thick/2)
                .faces(">Z")
                .workplane()
                .hole(dims.mount.dia)

                # Put the grub screw pilot at half height.
                .faces(">Z")
                .workplane(offset=-dims.mount.length/2)
                .transformed(rotate=(90,0,0))
                .circle(dims.pilot/2)
                .cutBlind(dims.mount.dia+dims.thick)

                # Now add holes for the zip ties.
                # Space them dims.thick apart (eh, because), and import the
                # entirety of numpy for one fucking function since the range builtin only does ints.
                .faces("<Y[1]")
                .workplane()
                .pushPoints([(s*x, 0) for s in (1, -1)
                                      for x in np.arange(dims.mount.dia/2 + dims.thick*1.5,
                                                         dims.holder.length/2 - dims.thick/2,
                                                         dims.thick)])
                .hole(dims.pilot)
            )

    return result


cs.clear()

dims = cs.Dims('scripts/household/watchwind.yml')
obj = build(dims)
cs.showsave(obj, dims)
