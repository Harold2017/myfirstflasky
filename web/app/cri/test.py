import pandas as pd
import math
import numpy as np
import os


with open('../uploads/test.txt') as f:
    data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
    f.close()
w = [i[0] for i in data.values]
s = [i[1] for i in data.values]


def cie_xyz(w, s):
    h = 6.6260693 * math.exp(-34)
    c = 299792458
    k = 1.3806505 * math.exp(-23)
    c1 = 2 * math.pi * h * c ** 2
    c2 = h * c / k
    #path = os.path.abspath("app") + "\\cri\\CIE31_1.txt"
    with open('CIE31_1.txt') as f:
        data = f.readlines()
        f.close()

    wl = data[0]
    x = data[1]
    y = data[2]
    z = data[3]
    T = data[4]

    xbar = np.interp(w, wl, x)
    for x in xbar:
        if np.isnan(x):
            x = 0.0
    print(xbar)
    ybar = np.interp(w, wl, y)
    zbar = np.interp(w, wl, z)

    X = np.trapz(w, np.dot(s, xbar))
    Y = np.trapz(w, np.dot(s, ybar))
    Z = np.trapz(w, np.dot(s, zbar))

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    u = 4 * x / (-2 * x + 12 * y + 3)
    v = 6 * y / (-2 * x + 12 * y + 3)
    return x, y, u, v


if __name__ == '__main__':
    cie_xyz(w, s)
