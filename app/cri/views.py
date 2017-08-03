from flask import render_template, flash, request, current_app, redirect, url_for
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
    user_file = User_files(author_id=current_user.id)
    return render_template('upload.html', user_file=user_file)


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
        return "Please choose one file to upload!"
        #result = request.args.get['file']
        #return result


@cri.route('/v1.0/chart')
@login_required
def cri_chart():
    author_id = current_user.id
    user_file = User_files.query.filter_by(author_id=author_id).order_by(User_files.id.desc()).first()
    file_path = user_file.file_path
    if file_path is None:
        flash('No Spectrum is uploaded!')
        return render_template('404.html'), 404
    with open(file_path) as f:
        data = pd.read_csv(f, sep="\t" or ' ' or ',', header=None)
        #data = f.readlines()
        f.close()

    if len(data) is 0:
        flash('No data is uploaded!')

    line = Line(title="Spectrum", width=800, height=400)

    attr = line.pdcast(data.ix[:, [0]])
    d = line.pdcast(data.ix[:, [1]])
    x = []
    y = []
    for i in d[0]:
        y.extend(i)
    for i in attr[0]:
        x.extend(i)
    line.add("Spectrum", x, y, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
             mark_point=["min", "max"])
    path = os.path.abspath("app/templates") + "\\cri_render.html"
    line.render(path)

    return render_template('cri_chart.html')






