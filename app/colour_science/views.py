from flask import flash, url_for, jsonify, render_template, request
from . import colour_science
import numpy as np
from matplotlib import pylab
from io import StringIO
import colour
from colour.plotting import chromaticity_diagram_plot_CIE1931, multi_colour_swatches_plot, ColourSwatch
from .forms import LabForm

'''
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
'''


@colour_science.route('/Lab', methods=['GET', 'POST'])
def lab_plot():
    if request.method == 'POST':
        data = request.get_json()
        data = [float(i) for i in data]
        Lab_list = [data[i + 1:i + 4] for i in range(0, len(data), 4)]
        cie_1931 = cie1931(Lab_list)
        swatchcolor = swatch_color(Lab_list)
        # print(cie_1931)
        # print(swatchcolor)
        return render_template('lab_plot_plotting.html', cie1931=cie_1931, swatch_color=swatchcolor)
    return render_template('lab_plot_datatables.html')


def cie1931(Lab_list):
    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    cnt = 1
    for Lab in Lab_list:
        xy = colour.XYZ_to_xy(colour.Lab_to_XYZ(np.array(Lab)))
        x, y = xy
        pylab.plot(x, y, 'o', markersize=5, markeredgewidth=1, markerfacecolor="None", markeredgecolor='black')
        '''
        pylab.annotate((("%.4f" % x), ("%.4f" % y)),
                       xy=xy,
                       xytext=(-50, 30),
                       textcoords='offset points',
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=-0.2'))
        '''
        pylab.text(x, y, str(cnt), fontsize=10)
        cnt = cnt + 1

    a = pylab.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    pylab.close(a)
    del a
    return figdata_svg


def swatch_color(Lab_list):
    swatches = []
    counter = 1
    for Lab in Lab_list:
        RGB = abs(colour.XYZ_to_sRGB(colour.Lab_to_XYZ(np.array(Lab))))
        '''
        # RGB shows a wrong color? sRGB is correct
        illuminant_XYZ = np.array([0.34570, 0.35850])
        illuminant_RGB = np.array([0.31270, 0.32900])
        XYZ_to_RGB_matrix = np.array(
            [[3.24062548, -1.53720797, -0.49862860],
             [-0.96893071, 1.87575606, 0.04151752],
             [0.05571012, -0.20402105, 1.05699594]]
        )
        # chromatic_adaptation_transform = 'Bradford'
        RGB = colour.XYZ_to_RGB(colour.Lab_to_XYZ(np.array(Lab)), illuminant_XYZ, illuminant_RGB, XYZ_to_RGB_matrix)
        '''
        title = 'sample_' + str(counter)
        swatches.append(ColourSwatch(title, RGB))
        counter = counter + 1
    multi_colour_swatches_plot(swatches, text_size=8, standalone=False, figure_size=(4, 6))
    b = pylab.gcf()
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    pylab.close(b)
    del b
    return figdata_svg_b
