from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import User_files
from .. import db
from . import cri
from werkzeug.utils import secure_filename
from pyecharts import Line
import os

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, SelectMultipleField
from pytz import timezone

from colour.plotting import CIE_1931_chromaticity_diagram_plot, single_spd_plot, multi_spd_plot,\
    single_spd_colour_rendering_index_bars_plot
from colour import CMFS, ILLUMINANTS_RELATIVE_SPDS, SpectralPowerDistribution, spectral_to_XYZ, XYZ_to_xy,\
    xy_to_CCT, colour_rendering_index
import pandas as pd
import pylab
from io import StringIO
import matplotlib.pyplot as plot
import numpy as np


tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')

upload_folder = os.path.abspath("app") + "\\uploads"
extensions = set(['csv', 'txt', 'png', 'jpg', 'jpeg'])


class SelectSpectrumForm(FlaskForm):
    spectra = SelectField('Sensors', coerce=int)
    submit = SubmitField('Plot Data')

    def __init__(self, spectrum, *args, **kwargs):
        super(SelectSpectrumForm, self).__init__(*args, **kwargs)
        self.spectra.choices = [(spectra.id, spectra.timestamp) for spectra in spectrum]
        self.spectrum = spectrum


class SelectMultipleSpectrumForm(FlaskForm):
    spectra = SelectMultipleField('Spectrum', coerce=int)
    submit = SubmitField('Plot multi-spectrum')

    def __init__(self, spectrum, *args, **kwargs):
        super(SelectMultipleSpectrumForm, self).__init__(*args, **kwargs)
        self.spectra.choices = [(spectra.id, spectra.timestamp) for spectra in spectrum]
        self.spectrum = spectrum


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


#@cri.before_request
#def before_request():
#    if request.path != '/':
#        if request.headers['content-type'].find('application/json'):
#            return 'Unsupported Media Type', 415


@cri.route('/v1.0')
@login_required
def upload():
    user_file = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).first()
    if user_file:
        file_path = user_file.file_path
        if file_path is None:
            flash('No Spectrum is uploaded!')
            return render_template('404.html'), 404
    else:
        user_file = 0
        chart = 0
        return render_template('upload.html', user_file=user_file, chart=chart)
    user_file = 1
    return render_template('upload.html', user_file=user_file, cie1931=cie1931())


@cri.route('/v1.0/upload', methods=['GET', 'POST'])
@login_required
def upload_spectrum():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            user_file = User_files(author_id=current_user.id)
            user_file.file_path = file_path
            db.session.add(user_file)
            db.session.commit()
            flash("Your spectrum has been uploaded!")
            return redirect(url_for('cri.cri_chart'))
    else:
        pass
        return render_template('no_file.html', user=current_user)
        #result = request.args.get['file']
        #return result


@cri.route('/v1.0/chart', methods=['GET', 'POST'])
@login_required
def cri_chart():
    if User_files.query.filter_by(author_id=current_user.id).first():
        spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
        form = SelectMultipleSpectrumForm(spectrum)
        #chart = 0
        spd = 0
        cie_1931 = 0
    else:
        form = 0
        #chart = 0
        spd = 0
        cie_1931 = 0
    if form.validate_on_submit():
        spectrum = form.spectra.data
        if len(spectrum) == 1:
            cie_1931 = cie1931(spectrum)
            spd = 0
        else:
            file_path = []
            for spectra in spectrum:
                user_file = User_files.query.filter_by(id=spectra).first()
                file_path.append(user_file.file_path)
            spd = multiple(file_path)
            cie_1931 = 0
        '''line = Line(width=800, height=400)
        for spectra in spectrum:
            user_file = User_files.query.filter_by(id=spectra).first()
            file_path = user_file.file_path
            title = user_file.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')
            if file_path is None:
                flash('No Spectrum is uploaded!')
                return render_template('404.html'), 404
            with open(file_path) as f:
                data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
                f.close()

            if len(data) is 0:
                flash('No data is uploaded!')

            attr = [i[0] for i in data.values]
            d = [i[1] for i in data.values]
            line.add(title, x_axis=attr, y_axis=d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
                     mark_point=["min", "max"])
        chart = line.render_embed()'''
    spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
    form = SelectMultipleSpectrumForm(spectrum)
    #return render_template('cri_chart.html', form=form, chart=chart)
    return render_template('cri_chart.html', form=form, spd=spd, cie1931=cie_1931)


def line_chart(*args):
    if not args:
        author_id = current_user.id
        user_file = User_files.query.filter_by(author_id=author_id).order_by(User_files.id.desc()).first()
        file_path = user_file.file_path
    else:
        file = User_files.query.filter_by(id=args).first()
        file_path = file.file_path
    if file_path is None:
        flash('No Spectrum is uploaded!')
        return render_template('404.html'), 404
    with open(file_path) as f:
        data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
        f.close()

    if len(data) is 0:
        flash('No data is uploaded!')

    line = Line(title="Spectrum", width=800, height=400)

    attr = [i[0] for i in data.values]
    d = [i[1] for i in data.values]
    #from .test import cie_xyz
    #output = cie_xyz(attr, d)
    line.add("Spectrum", x_axis=attr, y_axis=d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
             mark_point=["min", "max"])
    #root = os.path.abspath("app/templates")
    #path = root + "\\cri_render.html"
    return line.render_embed()#, output
    #line.render(path)


def cie1931(*args):
    cmfs = CMFS['CIE 1931 2 Degree Standard Observer']
    if not args:
        author_id = current_user.id
        user_file = User_files.query.filter_by(author_id=author_id).order_by(User_files.id.desc()).first()
        file_path = user_file.file_path
    else:
        file = User_files.query.filter_by(id=args).first()
        file_path = file.file_path
    if file_path is None:
        flash('No Spectrum is uploaded!')
        return render_template('404.html'), 404
    with open(file_path) as f:
        data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
        f.close()

    if len(data) is 0:
        flash('No data is uploaded!')
        valid = 0
    valid = 1
    w = [i[0] for i in data.values]
    s = [i[1] for i in data.values]
    data_formated = dict(zip(w, s))
    spd = SpectralPowerDistribution('Sample', data_formated)
    b = single_spd_plot(spd, standalone=False, figure_size=(5, 5), title='Spectrum')
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    plot.close(b)
    illuminant = ILLUMINANTS_RELATIVE_SPDS['D50']
    XYZ = spectral_to_XYZ(spd, cmfs, illuminant)
    xy = XYZ_to_xy(XYZ)

    CIE_1931_chromaticity_diagram_plot(standalone=False, figure_size=(5, 5), grid=False,
                                       title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    x, y = xy
    pylab.plot(x, y, 'o-', color='white')
    pylab.annotate((("%.4f" % x), ("%.4f" % y)),
                   xy=xy,
                   xytext=(-50, 30),
                   textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=-0.2'))

    a = plot.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    plot.close(a)

    cct = round(xy_to_CCT(xy))
    cri_all = colour_rendering_index(spd, additional_data=True)
    cri = cri_all.Q_a
    Q_as = cri_all.Q_as
    cris = [s[1].Q_a for s in sorted(Q_as.items(), key=lambda s: s[0])]
    cris = cris[:9]
    single_spd_colour_rendering_index_bars_plot(spd, standalone=False, figure_size=(7, 7),
                                                title='Colour rendering index')
    c = plot.gcf()
    figfile_c = StringIO()
    c.savefig(figfile_c, format='svg')
    figfile_c.seek(0)
    figdata_svg_c = '<svg' + figfile_c.getvalue().split('<svg')[1]
    c.clf()
    plot.close(c)

    fig = pylab.figure('CRI Radar Map', figsize=(5, 5))
    titles = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9']
    labels = [
        [20, 40, 60, 80, 100],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]

    radar = Radar(fig, titles, labels)
    radar.plot(cris, "--", lw=2, color="k", alpha=0.6, label="R1-9")
    radar.ax.legend()
    d = pylab.gcf()
    figfile_d = StringIO()
    d.savefig(figfile_d, format='svg')
    figfile_d.seek(0)
    figdata_svg_d = '<svg' + figfile_d.getvalue().split('<svg')[1]
    d.clf()
    pylab.close(d)

    x = round(x, 4)
    y = round(y, 4)
    xy = [x, y]
    del a, b, c, d
    return figdata_svg, valid, xy, figdata_svg_b, figdata_svg_c, cct, cri, figdata_svg_d


def multiple(args):
    cmfs = CMFS['CIE 1931 2 Degree Standard Observer']
    spd = []
    for d in args:
        with open(d) as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()
        w = [i[0] for i in data.values]
        s = [i[1] for i in data.values]
        data_formated = dict(zip(w, s))
        spd.append(SpectralPowerDistribution('Sample', data_formated))
    b = multi_spd_plot(spd, standalone=False, figure_size=(5, 5), title='Spectrum')
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    plot.close(b)

    CIE_1931_chromaticity_diagram_plot(standalone=False, figure_size=(5, 5), grid=False,
                                       title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    illuminant = ILLUMINANTS_RELATIVE_SPDS['D50']
    for s in spd:
        XYZ = spectral_to_XYZ(s, cmfs, illuminant)
        xy = XYZ_to_xy(XYZ)
        print(xy)

        x, y = xy
        pylab.plot(x, y, 'o-', alpha=0.5)
        pylab.annotate((("%.4f" % x), ("%.4f" % y)),
                       xy=xy,
                       xytext=(-50, 30),
                       textcoords='offset points',
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=-0.2'))

    a = plot.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    plot.close(a)
    del a, b
    return figdata_svg, figdata_svg_b


class Radar(object):
    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.9, 0.88]

        self.n = len(titles)
        self.angles = np.arange(90, 90 + 360, 360.0 / self.n)
        self.angles = [a % 360 for a in self.angles]
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i)
                     for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=14)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(20, 101, 20), angle=angle, labels=label)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 100)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)

