from functools import partial

import colour
import numpy as np
from scipy import optimize


def delta_e(rgb1, rgb2):
    """Returns the CIEDE2000 difference between rgb1 and rgb2 (both sRGB with range 0-1).
    Reference: https://en.wikipedia.org/wiki/Color_difference#CIEDE2000."""
    lab1 = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb1))
    lab2 = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb2))
    return colour.delta_E_CIE2000(lab1, lab2)


def opfunc_(x, loss, eps=1e-8):
    """Given a loss function i.e. delta_e(), returns the loss and gradient at a point x. The
    gradient is computed by finite difference."""
    grad = np.zeros_like(x)
    eye = np.eye(len(x))
    for i in range(len(x)):
        fx = loss(x)
        grad[i] = (loss(x + eps*eye[i]) - fx) / eps
    return fx, grad


def gamut_map(rgb):
    """Finds the nearest in-gamut color to an out-of-gamut color using delta_e() as its measure of
    difference."""
    x = np.clip(rgb, 0, 1)
    if (rgb == x).all():
        return x
    loss = partial(delta_e, rgb)
    opfunc = partial(opfunc_, loss=loss)
    x, _, _ = optimize.fmin_l_bfgs_b(opfunc, x, bounds=[(0, 1)]*3)
    return x