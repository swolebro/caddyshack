"""Some shortcuts for geometric and trig functions."""

# TODO: Look into existing libraries for this type of stuff.
# A cursory ready of the API's for shapely and sympy.geometry showed
# they were in the right ballpark, but the kinds of stupid calculations
# I've had to do for parametric CAD.

# TODO: Wouldn't it be nice if you could have an object, like a RegularPolygon,
# which you initialize with some subset of its measurements (eg. apothem and
# number of sides, or vertex angle and edge length) and it filled in the rest
# for you, or raised an error if you didn't provide enough information?
# Would need to think about how to do that cleverly (ie. non disgustingly).

import numpy as np


def circumscribe(n=6, *, side=None, apo=None, wrench=None):
    """Return the diameter of the circle that circumscribes the a regular
    n-gon with side s or apothem a. For even n, you can provide the wrench
    size, which is 2*apothem."""

    if wrench is not None:
        if n % 2:
            raise Exception("wrench parameter invalid for uneven n (%d)" % n)

        apo = wrench/2

    if apo is not None:
        return 2*apo/np.cos(np.pi/n)

    if side is not None:
        return side/np.sin(np.pi/n)

    raise Exception("Must provide one of side, apo, or wrench.")


