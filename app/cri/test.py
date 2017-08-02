import pandas as pd
import math
import numpy as np


def cie_xyz(w, s):
    h = 6.6260693 * math.exp(-34)
    c = 299792458
    k = 1.3806505 * math.exp(-23)
    c1 = 2 * math.pi * h * c ** 2
    c2 = h * c / k
    with open('CIE31_1') as f:
        data = f.readlines()
        f.close()

    wl = data[0]
    x = data[1]
    y = data[2]
    z = data[3]
    T = data[4]

    xbar = np.interp(w, wl, x)
    ybar = np.interp(w, wl, y)
    zbar = np.interp(w, wl, z)

    X = np.trapz(w, np.dot(s, xbar))
    Y = np.trapz(w, np.dot(s, ybar))
    Z = np.trapz(w, np.dot(s, zbar))

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    u = 4 * x / (-2 * x + 12 * y + 3)
    v = 6 * y / (-2 * x + 12 * y + 3)