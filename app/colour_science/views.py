from flask import flash, url_for, jsonify, render_template
from . import colour_science
import numpy as np
from matplotlib import pylab
from io import StringIO
import colour
from colour.plotting import chromaticity_diagram_plot_CIE1931, single_colour_swatch_plot, ColourSwatch
from .forms import LabForm


@colour_science.route('/Lab', methods=['GET', 'POST'])
def lab_plot():
    form = LabForm()
    cie_1931 = None
    swatchcolor = None
    if form.validate_on_submit():
        L = form.L.data
        a = form.a.data
        b = form.b.data

        Lab = np.array([L, a, b])
        XYZ = colour.Lab_to_XYZ(Lab)
        xy = colour.XYZ_to_xy(XYZ)

        cie_1931 = cie1931(xy)
        swatchcolor = swatch_color(XYZ)
    return render_template('lab_plot.html', form=form, cie1931=cie_1931, swatch_color=swatchcolor)


def cie1931(xy):
    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    x, y = xy
    pylab.plot(x, y, 'o', markersize=7, markeredgewidth=1, markerfacecolor="None", markeredgecolor='black')
    pylab.annotate((("%.4f" % x), ("%.4f" % y)),
                   xy=xy,
                   xytext=(-50, 30),
                   textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=-0.2'))

    a = pylab.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    pylab.close(a)
    del a
    return figdata_svg


def swatch_color(XYZ):
    RGB = colour.XYZ_to_sRGB(XYZ)
    title = str(RGB)
    single_colour_swatch_plot(ColourSwatch(title, RGB), text_size=8, standalone=False, figure_size=(4, 6))
    b = pylab.gcf()
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    pylab.close(b)
    del b
    return figdata_svg_b
