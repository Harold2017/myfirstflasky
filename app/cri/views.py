from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import User_files
from .. import db
from . import cri
from werkzeug.utils import secure_filename
from pyecharts import Line
import os
import pandas as pd
#import math
#import numpy as np


upload_folder = os.path.abspath("app") + "\\uploads"
extensions = set(['csv', 'txt', 'png', 'jpg', 'jpeg'])


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
    user_file = User_files(author_id=current_user.id)
    return render_template('upload.html', user_file=user_file, chart=line_chart())


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


@cri.route('/v1.0/chart')
@login_required
def cri_chart():
    return render_template('cri_chart.html', chart=line_chart())


def line_chart():
    author_id = current_user.id
    user_file = User_files.query.filter_by(author_id=author_id).order_by(User_files.id.desc()).first()
    file_path = user_file.file_path
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
    line.add("Spectrum", x_axis=attr, y_axis=d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
             mark_point=["min", "max"])
    #root = os.path.abspath("app/templates")
    #path = root + "\\cri_render.html"
    return line.render_embed()
    #line.render(path)






