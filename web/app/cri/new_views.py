from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import User_files
from .. import db
from . import cri
from werkzeug.utils import secure_filename
import os

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, SelectMultipleField
from pytz import timezone

from colour.plotting import chromaticity_diagram_plot_CIE1931, single_spd_plot, multi_spd_plot, \
    single_spd_colour_rendering_index_bars_plot
from colour import CMFS, ILLUMINANTS_RELATIVE_SPDS, SpectralPowerDistribution, spectral_to_XYZ, XYZ_to_xy, \
    xy_to_CCT, colour_rendering_index, UCS_uv_to_xy, CCT_to_uv, UCS_to_uv, XYZ_to_UCS
import pandas as pd
import pylab
from io import StringIO
import matplotlib.pyplot as plot
from matplotlib.collections import PolyCollection
import numpy as np
from math import sqrt
from flask_table import Table, Col
from pyecharts import Line

# from scipy.interpolate import Akima1DInterpolator
# from scipy import interpolate

tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')

upload_folder = os.path.abspath("app") + "\\uploads"
extensions = {'csv', 'txt'}


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


class SelectMultiplePlots(FlaskForm):
    plot = SelectMultipleField('Plots', choices=[('1', 'Spectrum'), ('2', 'CIE 1931 diagram'),
                                                 ('3', 'CRI diagram')])
    submit = SubmitField('Show plots')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


@cri.route('/v1.0', methods=['GET', 'POST'])
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
        return render_template('cri_upload.html', user_file=user_file, table=0, form=0)
    user_file = 1
    spd, valid = SPD()
    if valid:
        table = parameters_table(spd)
        form = SelectMultiplePlots()
    else:
        table = 0
        form = 0
    if form.validate_on_submit():
        Plots = form.plot.data
        choices = []
        for plot in Plots:
            choices.append(plot)
        spd = SPD()[0]
        xy, cct, Duv, SDCM, cri, cris = parameters(spd)
        if len(choices) == 3:
            spd_p = spd_plot(spd)
            cie1931_p = cie1931(xy)
            sdcm_p = sdcm_plot(xy)
            cri_p = cri_plot(spd)
            radar_p = radar_plot(cris)
            return render_template('cri_plot.html', spd_p=spd_p, cie1931_p=cie1931_p,
                                   sdcm_p=sdcm_p, cri_p=cri_p, radar_p=radar_p)
        elif len(choices) == 2:
            if '1' in choices and '2' in choices:
                spd_p = spd_plot(spd)
                cie1931_p = cie1931(xy)
                sdcm_p = sdcm_plot(xy)
                return render_template('cri_plot.html', spd_p=spd_p, cie1931_p=cie1931_p,
                                       sdcm_p=sdcm_p, cri_p=0, radar_p=0)
            elif '1' in choices and '3' in choices:
                spd_p = spd_plot(spd)
                cri_p = cri_plot(spd)
                radar_p = radar_plot(cris)
                return render_template('cri_plot.html', spd_p=spd_p, cie1931_p=0,
                                       sdcm_p=0, cri_p=cri_p, radar_p=radar_p)
            elif '2' in choices and '3' in choices:
                cie1931_p = cie1931(xy)
                sdcm_p = sdcm_plot(xy)
                cri_p = cri_plot(spd)
                radar_p = radar_plot(cris)
                return render_template('cri_plot.html', spd_p=0, cie1931_p=cie1931_p,
                                       sdcm_p=sdcm_p, cri_p=cri_p, radar_p=radar_p)
        elif len(choices) == 1:
            if '1' in choices:
                spd_p = spd_plot(spd)
                return render_template('cri_plot.html', spd_p=spd_p, cie1931_p=0,
                                       sdcm_p=0, cri_p=0, radar_p=0)
            elif '2' in choices:
                cie1931_p = cie1931(xy)
                sdcm_p = sdcm_plot(xy)
                return render_template('cri_plot.html', spd_p=0, cie1931_p=cie1931_p,
                                       sdcm_p=sdcm_p, cri_p=0, radar_p=0)
            elif '3' in choices:
                cri_p = cri_plot(spd)
                radar_p = radar_plot(cris)
                return render_template('cri_plot.html', spd_p=0, cie1931_p=0,
                                       sdcm_p=0, cri_p=cri_p, radar_p=radar_p)
    return render_template('cri_upload.html', user_file=user_file, table=table, form=form)


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


@cri.route('/v1.0/mccree', methods=['GET', 'POST'])
@login_required
def choose_file():
    if User_files.query.filter_by(author_id=current_user.id).first():
        spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
        form = SelectMultipleSpectrumForm(spectrum)
        mccree_l = 0
    else:
        form = 0
        mccree_l = 0
    if form.validate_on_submit():
        spectrum = form.spectra.data
        if len(spectrum) == 1:
            mccree_l = mccree(spectrum)
        else:
            '''file_path = []
            for spectra in spectrum:
                user_file = User_files.query.filter_by(id=spectra).first()
                file_path.append(user_file.file_path)
            mccree_l = multiple_mccree(file_path)'''
            pass
    spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
    form = SelectMultipleSpectrumForm(spectrum)
    return render_template('cri_mccree.html', form=form, mccree=mccree_l)


def mccree(spd):
    # LARGE_FONT = ("Verdana", 12)
    # Smooth_Points_Number = 50
    file = User_files.query.filter_by(id=spd).first()
    file_path = file.file_path
    (dirpath, tempfilename) = os.path.split(file_path)
    (filename, extension) = os.path.splitext(tempfilename)
    if file_path is None:
        flash('No Spectrum is uploaded!')
        return render_template('404.html'), 404
    try:
        with open(file_path, encoding='utf-8') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()
    except UnicodeDecodeError:
        with open(file_path, encoding='utf-16') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()

    w = [i[0] for i in data.values]
    s = [i[1] for i in data.values]

    mccree_data = np.array([[3.25e+02, 0.00e+00],
                            [3.50e+02, 1.50e-01],
                            [3.75e+02, 4.00e-01],
                            [4.00e+02, 6.60e-01],
                            [4.25e+02, 7.70e-01],
                            [4.50e+02, 7.50e-01],
                            [4.75e+02, 6.90e-01],
                            [5.25e+02, 7.40e-01],
                            [5.50e+02, 8.80e-01],
                            [5.90e+02, 1.00e+00],
                            [6.25e+02, 1.00e+00],
                            [6.50e+02, 9.40e-01],
                            [6.75e+02, 9.30e-01],
                            [7.00e+02, 4.20e-01],
                            [7.50e+02, 4.00e-02],
                            [7.75e+02, 0.00e+00]])
    wavelength = np.array(mccree_data[:, 0])
    spectrum = np.array(normalize(mccree_data[:, 1]))
    wl = len(w)
    wmin = min(w)
    wmax = max(w)
    intermin = wmin if wmin < wavelength.min() else wavelength.min()
    intermax = wmax if wmax > wavelength.max() else wavelength.max()
    wavelength_smooth = np.linspace(intermin, intermax, wl)
    # akima = Akima1DInterpolator(wavelength, spectrum)
    line = Line(title='Mccree Comparision', width=800, height=400)
    attr = wavelength_smooth
    d = np.interp(wavelength_smooth, wavelength, spectrum)
    line.add("Mccree", attr, d, is_smooth=True, is_fill=True, line_opacity=0.2,
             area_opacity=0.4, symbol=True, is_datazoom_show=True)
    line.add(filename, attr, s, is_smooth=True, is_fill=True, line_opacity=0.2,
             area_opacity=0.4, symbol=True, is_datazoom_show=True)
    chart = line.render_embed()
    area_under_mccree = np.trapz(d, attr)
    area_under_tmp = np.trapz(w, s)
    percentage = str(abs(round(area_under_tmp / area_under_mccree * 100, 2))) + ' %'
    return render_template('sensor_render_pyecharts.html', chart=chart), percentage


def multiple_mccree(file_path):
    pass


def normalize(v):
    norm = v.max()
    if norm == 0:
        return v
    return v / norm


@cri.route('/v1.0/chart', methods=['GET', 'POST'])
@login_required
def cri_chart():
    if User_files.query.filter_by(author_id=current_user.id).first():
        spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
        form = SelectMultipleSpectrumForm(spectrum)
        spd = 0
        cie_1931 = 0
    else:
        form = 0
        spd = 0
        cie_1931 = 0
    if form.validate_on_submit():
        spectrum = form.spectra.data
        if len(spectrum) == 1:
            cie_1931 = cie1931_all(spectrum)
            spd = 0
        else:
            file_path = []
            for spectra in spectrum:
                user_file = User_files.query.filter_by(id=spectra).first()
                file_path.append(user_file.file_path)
            spd = multiple(file_path)
            cie_1931 = 0
    spectrum = User_files.query.filter_by(author_id=current_user.id).order_by(User_files.id.desc()).all()
    form = SelectMultipleSpectrumForm(spectrum)
    return render_template('cri_chart.html', form=form, spd=spd, cie1931=cie_1931)


def SPD(*args):
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
    try:
        with open(file_path, encoding='utf-8') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()
    except UnicodeDecodeError:
        with open(file_path, encoding='utf-16') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()

    if len(data) is 0:
        flash('No data is uploaded!')
        spd = 0
        valid = 0
    else:
        valid = 1
        w = [float(i[0].split()[0]) if isinstance(i[0], str) else i[0] for i in data.values.tolist()]
        s = [float(i[0].split()[1]) if isinstance(i[0], str) else i[1] for i in data.values.tolist()]
        data_formated = dict(zip(w, s))
        spd = SpectralPowerDistribution('Sample', data_formated)
    return spd, valid


def parameters(spd):
    cmfs = CMFS['CIE 1931 2 Degree Standard Observer']
    illuminant = ILLUMINANTS_RELATIVE_SPDS['D50']
    XYZ = spectral_to_XYZ(spd, cmfs, illuminant)
    xy = XYZ_to_xy(XYZ)
    x, y = xy
    u, v = (UCS_to_uv(XYZ_to_UCS(XYZ)))
    cct = xy_to_CCT(xy)
    u0, v0 = CCT_to_uv(cct, 'Robertson 1968', D_uv=0)
    Duv = round(sqrt((u - u0) ** 2 + (v - v0) ** 2), 4)
    cct_r = round(xy_to_CCT(xy))
    SDCM = sdcm(x, y, cct_r)
    cri_all = colour_rendering_index(spd, additional_data=True)
    cri = round(cri_all.Q_a, 1)
    Q_as = cri_all.Q_as
    cris = [s[1].Q_a for s in sorted(Q_as.items(), key=lambda s: s[0])]
    return xy, cct, Duv, SDCM, cri, cris


class ItemTable(Table):
    factor = Col('Factor')
    classes = ['table', 'table-bordered']
    value = Col('Value')


class Item(object):
    def __init__(self, factor, value):
        self.factor = factor
        self.value = value


def parameters_table(spd):
    xy, cct, Duv, SDCM, cri, cris = parameters(spd)
    x, y = xy
    x = round(x, 4)
    y = round(y, 4)
    cct = round(cct, 1)
    Duv = round(Duv, 4)
    items = [dict(factor='x', value=x),
             dict(factor='y', value=y),
             dict(factor='CCT', value=cct),
             dict(factor='Ra', value=cri),
             dict(factor='Duv', value=Duv),
             dict(factor='SDCM', value=SDCM)]
    table = ItemTable(items)
    return table


def spd_plot(spd):
    b = single_spd_plot(spd, standalone=False, figure_size=(5, 5), title='Spectrum')
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    plot.close(b)
    del b
    return figdata_svg_b


def cie1931(xy):
    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    start, end = 1667, 100000
    mn = np.array(
        [UCS_uv_to_xy(CCT_to_uv(m, 'Robertson 1968', D_uv=0))
         for m in np.arange(start, end + 250, 250)])

    pylab.plot(mn[..., 0], mn[..., 1], color='black', linewidth=2)

    for i in (2500, 3000, 4000, 5000, 6000, 7000):
        x0, y0 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=-0.025))
        x1, y1 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=0.025))
        pylab.plot((x0, x1), (y0, y1), color='black', linewidth=2)
        pylab.annotate(
            '{0}K'.format(i),
            xy=(x0, y0),
            xytext=(0, -i / 250),
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

    a = plot.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    plot.close(a)
    del a
    return figdata_svg


def sdcm_plot(xy):
    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='C78.377-2008, Tolerance Quadrangle',
                                      bounding_box=(0.25, 0.5, 0.25, 0.45))

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
            xytext=(0, -i / 250),
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
    e = pylab.gcf()
    figfile_e = StringIO()
    e.savefig(figfile_e, format='svg')
    figfile_e.seek(0)
    figdata_svg_e = '<svg' + figfile_e.getvalue().split('<svg')[1]
    e.clf()
    pylab.close(e)
    del e
    return figdata_svg_e


def cri_plot(spd):
    single_spd_colour_rendering_index_bars_plot(spd, standalone=False, figure_size=(7, 7),
                                                title='Colour rendering index')
    c = plot.gcf()
    figfile_c = StringIO()
    c.savefig(figfile_c, format='svg')
    figfile_c.seek(0)
    figdata_svg_c = '<svg' + figfile_c.getvalue().split('<svg')[1]
    c.clf()
    plot.close(c)
    del c
    return figdata_svg_c


def radar_plot(cris):
    cris = cris[:9]
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
    del d
    return figdata_svg_d


def multiple(args):
    cmfs = CMFS['CIE 1931 2 Degree Standard Observer']
    spd = []
    for d in args:
        try:
            with open(d, encoding='utf-8') as f:
                data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
                f.close()
        except UnicodeDecodeError:
            with open(d, encoding='utf-16') as f:
                data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
                f.close()
        w = [float(i[0].split()[0]) if isinstance(i[0], str) else i[0] for i in data.values.tolist()]
        s = [float(i[0].split()[1]) if isinstance(i[0], str) else i[1] for i in data.values.tolist()]
        data_formated = dict(zip(w, s))
        spd.append(SpectralPowerDistribution('Sample', data_formated))
    b = multi_spd_plot(spd, standalone=False, figure_size=(5, 5), title='Spectrum')
    figfile_b = StringIO()
    b.savefig(figfile_b, format='svg')
    figfile_b.seek(0)
    figdata_svg_b = '<svg' + figfile_b.getvalue().split('<svg')[1]
    b.clf()
    plot.close(b)

    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    illuminant = ILLUMINANTS_RELATIVE_SPDS['D50']
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
            xytext=(0, -i / 250),
            color='black',
            textcoords='offset points',
            size='x-small')
    for s in spd:
        XYZ = spectral_to_XYZ(s, cmfs, illuminant)
        xy = XYZ_to_xy(XYZ)

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


def sdcm(x, y, Tc):
    sx = round(x, 3)
    sy = round(y, 3)

    if Tc <= 2850:
        SDCM = 400000 * (sx - 0.459) ** 2 - 2 * 195000 * (sx - 0.459) * (sy - 0.412) + 280000 * (sy - 0.412) ** 2
    elif Tc <= 3250:
        SDCM = 390000 * (sx - 0.44) ** 2 - 2 * 195000 * (sx - 0.44) * (sy - 0.403) + 275000 * (sy - 0.403) ** 2
    elif Tc <= 3750:
        SDCM = 380000 * (sx - 0.411) ** 2 - 2 * 200000 * (sx - 0.411) * (sy - 0.393) + 250000 * (sy - 0.393) ** 2
    elif Tc <= 4250:
        SDCM = 395000 * (sx - 0.38) ** 2 - 2 * 215000 * (sx - 0.38) * (sy - 0.38) + 260000 * (sy - 0.38) ** 2
    elif Tc <= 4750:
        SDCM = 460000 * (sx - 0.3611) ** 2 - 2 * 240000 * (sx - 0.3611) * (sy - 0.3658) + 270000 * (sy - 0.3658) ** 2
    elif Tc <= 5350:
        SDCM = 560000 * (sx - 0.346) ** 2 - 2 * 250000 * (sx - 0.346) * (sy - 0.359) + 280000 * (sy - 0.359) ** 2
    elif Tc <= 6100:
        SDCM = 760000 * (sx - 0.3287) ** 2 - 2 * 350000 * (sx - 0.3287) * (sy - 0.3417) + 380000 * (sy - 0.3417) ** 2
    elif Tc <= 7000:
        SDCM = 860000 * (sx - 0.313) ** 2 - 2 * 400000 * (sx - 0.313) * (sy - 0.337) + 450000 * (sy - 0.337) ** 2
    else:
        SDCM = 'NA'
    if SDCM != 'NA':
        SDCM = round(sqrt(SDCM), 1)
    return SDCM


def cie1931_all(*args):
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
    try:
        with open(file_path, encoding='utf-8') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()
    except UnicodeDecodeError:
        with open(file_path, encoding='utf-16') as f:
            data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
            f.close()

    w = [float(i[0].split()[0]) if isinstance(i[0], str) else i[0] for i in data.values.tolist()]
    s = [float(i[0].split()[1]) if isinstance(i[0], str) else i[1] for i in data.values.tolist()]
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

    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='CIE 1931 Chromaticity Diagram', bounding_box=(-0.1, 0.9, -0.05, 0.95))
    start, end = 1667, 100000
    mn = np.array(
        [UCS_uv_to_xy(CCT_to_uv(m, 'Robertson 1968', D_uv=0))
         for m in np.arange(start, end + 250, 250)])

    pylab.plot(mn[..., 0], mn[..., 1], color='black', linewidth=2)

    for i in (2500, 3000, 4000, 5000, 6000, 7000):
        x0, y0 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=-0.025))
        x1, y1 = UCS_uv_to_xy(CCT_to_uv(i, 'Robertson 1968', D_uv=0.025))
        pylab.plot((x0, x1), (y0, y1), color='black', linewidth=2)
        pylab.annotate(
            '{0}K'.format(i),
            xy=(x0, y0),
            xytext=(0, -i / 250),
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

    a = plot.gcf()
    figfile = StringIO()
    a.savefig(figfile, format='svg')
    figfile.seek(0)
    figdata_svg = '<svg' + figfile.getvalue().split('<svg')[1]
    a.clf()
    plot.close(a)

    cri_all = colour_rendering_index(spd, additional_data=True)
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

    chromaticity_diagram_plot_CIE1931(standalone=False, figure_size=(5, 5), grid=False,
                                      title='C78.377-2008, Tolerance Quadrangle',
                                      bounding_box=(0.25, 0.5, 0.25, 0.45))

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
            xytext=(0, -i / 250),
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
    e = pylab.gcf()
    figfile_e = StringIO()
    e.savefig(figfile_e, format='svg')
    figfile_e.seek(0)
    figdata_svg_e = '<svg' + figfile_e.getvalue().split('<svg')[1]
    e.clf()
    pylab.close(e)

    del a, b, c, d, e
    table = parameters_table(spd)
    return figdata_svg, figdata_svg_b, figdata_svg_c, \
           figdata_svg_d, figdata_svg_e, table
