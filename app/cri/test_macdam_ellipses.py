from colour.plotting import CIE_1931_chromaticity_diagram_plot, planckian_locus_CIE_1931_chromaticity_diagram_plot
from colour import CMFS, ILLUMINANTS_RELATIVE_SPDS, SpectralPowerDistribution, spectral_to_XYZ, XYZ_to_xy, \
    xy_to_CCT, colour_rendering_index, UCS_uv_to_xy, CCT_to_uv
import pandas as pd
import pylab
import matplotlib.pyplot as plot
import numpy as np
from matplotlib.collections import PolyCollection

illuminant = ILLUMINANTS_RELATIVE_SPDS['D50']
cmfs = CMFS['CIE 1931 2 Degree Standard Observer']
with open('C:\\Users\\Harold\\Documents\\GitHub\\myfirstflasky\\app\\uploads\\test.txt') as f:
    data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
    f.close()

w = [i[0] for i in data.values]
s = [i[1] for i in data.values]
data_formated = dict(zip(w, s))
spd = SpectralPowerDistribution('Sample', data_formated)
XYZ = spectral_to_XYZ(spd, cmfs, illuminant)
xy = XYZ_to_xy(XYZ)

CIE_1931_chromaticity_diagram_plot(standalone=False, figure_size=(5, 5), grid=False,
                                   title='CIE 1931 Chromaticity Diagram',
                                   bounding_box=(0.2, 0.6, 0.2, 0.6))

start, end = 1667, 100000
ab = np.array(
        [UCS_uv_to_xy(CCT_to_uv(a, 'Robertson 1968', D_uv=0))
         for a in np.arange(start, end + 250, 250)])

pylab.plot(ab[..., 0], ab[..., 1], color='black', linewidth=2)

for i in (2500, 3000, 4000, 5000, 6000, 7000):
    x0, y0 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=-0.025))
    x1, y1 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=0.025))
    pylab.plot((x0, x1), (y0, y1), color='black', linewidth=2)
    pylab.annotate(
        '{0}K'.format(i),
        xy=(x0, y0),
        xytext=(0, -i/250),
        color='black',
        textcoords='offset points',
        size='x-small')

x, y = xy
pylab.plot(x, y, 'o-', color='white')
pylab.annotate((("%.4f" % x), ("%.4f" % y)),
               xy=xy,
               xytext=(-50, 30),
               textcoords='offset points',
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=-0.2'))

centers = [(0.4578, 0.4101), (0.4338, 0.4030), (0.4073, 0.3917), (0.3818, 0.3797), (0.3611, 0.3658),
           (0.3447, 0.3553), (0.3287, 0.3417), (0.3123, 0.3282)]
plot.scatter(*zip(*centers), marker='o', color='k', s=10)

verts = [((0.4813, 0.4319), (0.4562, 0.4260), (0.4373, 0.3893), (0.4593, 0.3944)),
         ((0.4562, 0.4260), (0.4299, 0.4165), (0.4147, 0.3814), (0.4373, 0.3893)),
         ((0.4299, 0.4165), (0.3996, 0.4015), (0.3889, 0.3690), (0.4147, 0.3814)),
         ((0.4006, 0.4044), (0.3736, 0.3874), (0.3670, 0.3578), (0.3898, 0.3716)),
         ((0.3736, 0.3874), (0.3548, 0.3736), (0.3512, 0.3465), (0.3670, 0.3578)),
         ((0.3551, 0.3760), (0.3376, 0.3616), (0.3366, 0.3369), (0.3515, 0.3487)),
         ((0.3376, 0.3616), (0.3207, 0.3462), (0.3222, 0.3243), (0.3366, 0.3369)),
         ((0.3205, 0.3481), (0.3028, 0.3304), (0.3068, 0.3113), (0.3221, 0.3261))]
coll = PolyCollection(verts, facecolor='None', edgecolor='k', zorder=2)
plot.gca().add_collection(coll)
plot.show()
