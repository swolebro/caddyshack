"""This makes a couple components for a Thein baffle dust collector,
using a standard 5 gallon bucket and 1-7/8" shopvac hose."""


import cadquery as cq
import caddyshack as cs

import math

def build_outlet(dims):
    do = dims.outlet

    base = (cq.Workplane("XY")
                .circle(do.flange.dia/2)
                .extrude(do.thick)
                .faces(">Z")
                .workplane()
                .polygon(3, do.flange.boltcirc,forConstruction=True)
                .vertices()
                .hole(do.flange.pilot)
                .faces(">Z")
                .workplane()
                .circle(do.fitting.max/2 + do.thick)
                .extrude(do.fitting.length - do.thick)
            )

    # To reinforce the adapter portion, we do a full loft,
    # then build three wedges, and take the intersection.
    reinf1 = (base.faces("<Z[1]")
                .workplane()
                .circle(do.flange.dia/2)
                .workplane(offset=do.fitting.length - do.thick)
                .circle(do.fitting.max/2 + do.thick)
                .loft(combine=False)
            )

    reinf2 = None
    for x in 0, 120, 240:
        reinf3 = (base.faces("<Z")
                .workplane()
                .move(-do.flange.dia/4, 0)
                .rect(do.flange.dia/2, do.thick*2)
                .extrude(-do.fitting.length, combine=False)
                .rotate((0,0,0),(0,0,1),x)
            )

        # My stupid way of avoiding if/else's to initialize shit.
        reinf2 = reinf3.union(reinf2 or reinf3)

    base = base.union(reinf2.intersect(reinf1))

    taper = (cq.Workplane("XY")
                .circle(do.fitting.min/2)
                .workplane(offset=do.fitting.length)
                .circle(do.fitting.max/2)
                .loft()
            )

    return base.cut(taper)

def build_inlet(dims):
    di = dims.inlet
    db = dims.bucket


    rhi = db.topdia/2 - db.slope*di.flange.offset
    rlo = db.topdia/2 - db.slope*(di.flange.offset+di.flange.height)

    ang = math.acos((rhi-di.fitting.max)/rhi)
    length = rhi*math.sin(ang)

    L = di.fitting.length+length+di.thick
    W = di.fitting.max+di.thick*2
    H = di.fitting.max + 2*di.thick

    # Quick check to see if this will clearly fit in the print bed...
    print("Approximate size of inlet print:")
    print("%.2f x %.2f x %2.f" %(L,W,H))

    inlet = (cq.Workplane("XY")
                .move(-di.thick, -di.thick)
                .rect(L, W, centered=False)
                .extrude(H)
            )

    taper = (inlet.faces(">X")
                .workplane()
                .circle(di.fitting.max/2)
                .workplane(offset=-di.fitting.length)
                .circle(di.fitting.min/2)
                .loft(combine=False)
                .faces("<X")
                .workplane()
                .circle(di.fitting.min/2)
                .extrude(length)
            )

    clip = (inlet.faces(">Z")
                .workplane(offset=-di.thick+di.clip.leave)
                .move(L/2 - di.clip.catch/2 - di.clip.depth/2, 0)
                .rect(di.clip.depth-di.clip.catch, di.clip.width)
                .extrude(di.clip.catch, combine=False)
                .faces(">Z")
                .workplane()
                .move(di.clip.catch/2, 0)
                .rect(di.clip.depth, di.clip.width)
                .extrude(di.thick)
            )

    bucket = (cq.Workplane("XY")
                .move(0, -rhi+di.fitting.max)
                .circle(rlo)
                .workplane(offset=H)
                .circle(rhi)
                .loft()
            )

    # How the fuck do I make mounting holes for this thing, along the
    # curved face the bucket is going to cut out, and aligned radially with
    # the bucket? FFS.

    # We'll loop over a couple angles and heights and make a rotate workplane
    # that's been displaced to where the center of the bucket was. Then we'll
    # extrude cylinders past that which we can later cut from the inlet.
    # This might leave a nick or two in the middle, but whatever. I'm not going
    # to write loop to only loop the outside screw holes.
    pilots = []
    adj = math.asin(di.thick/(2*rlo))
    for angle in [-adj, ang/3, 2*ang/3, ang+adj]:
        for h in [di.thick/2, H/2, H-di.thick/2]:

            p = (cq.Workplane("XZ")
                    .workplane(offset=rhi - di.fitting.max)
                    .transformed((0,0,180-math.degrees(angle)))
                    .workplane(offset=rlo) # don't move the workplane all the way
                                           # forward yet, or you won't get a clean hole
                    .move(0, h)
                    .circle(di.pilot/2)
                    .extrude(di.pdepth+db.slope*h)  # so add the last bit to the extrusion instead
                )
            pilots.append(p)

    inlet = inlet.fillet(di.thick/4)
    inlet = inlet.cut(bucket).cut(taper).cut(clip)

    for p in pilots:
        inlet = inlet.cut(p)

    return inlet

def build_support(dims):
    ds = dims.support
    db = dims.bucket

    rhi = db.topdia/2 - dims.bucket.slope*ds.offset
    rlo = db.topdia/2 - dims.bucket.slope*(ds.offset + ds.height)

    # Need to know this dimension for cutting the baffle sheet.
    print("Bucket diameter at baffle height: ", rhi)

    support = (cq.Workplane("XY")
                    .move(0, -ds.depth/2)
                    .rect(ds.width, ds.depth)
                    .extrude(ds.height)
                    .faces(">Z")
                    .workplane()
                    .hole(ds.pilot, ds.height/2)
                    .faces(">Y")
                    .workplane()
                    .rect(ds.width,ds.height)
                    .extrude(ds.depth) # make sure the bucket leaves a smooth face
                    .faces(">Y")
                    .workplane()
                    .move(0, -ds.height/4)
                    .hole(ds.pilot)
               )

    bucket = (cq.Workplane("XY")
                .move(0, -rlo)
                .circle(rlo)
                .workplane(offset=ds.height)
                .circle(rhi)
                .loft()
              )

    #cs.pretty(bucket)
    return support.intersect(bucket)


if __name__ == "__cq_freecad_module__":
    cs.clear()

    dims = cs.Dims('scripts/shop/vacbaffle.yml')

    # Some calculated dimensions.
    dims.bucket.slope = (dims.bucket.topdia - dims.bucket.botdia)/(2*dims.bucket.height)


    obj  = build_outlet(dims)
    obj.val().label = "outlet"
    cs.showsave(obj, dims)

    obj = build_inlet(dims)
    obj.val().label = "inlet"
    cs.showsave(obj, dims)

    obj  = build_support(dims)
    obj.val().label = "support"
    cs.showsave(obj, dims)
