from flask import render_template, flash, request, current_app
from flask_login import login_required, current_user
from ..models import User_files
from . import cri
from werkzeug import secure_filename
from pyecharts import Line
import os
import pandas as pd


upload_folder = current_app.config['UPLOAD_FOLDER ']
max_file_length = current_app.config['MAX_CONTENT_LENGTH']
extensions = current_app.config['ALLOWED_EXTENSIONS']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


#@cri.before_request
#def before_request():
#    if request.path != '/':
#        if request.headers['content-type'].find('application/json'):
#            return 'Unsupported Media Type', 415


@cri.route('/v1.0/getfile', methods=['GET', 'POST'])
#@login_required
def upload_spectrum():
    if request.method == 'POST':

        file = request.files['myfile']
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)

        file.save(file_path)
        current_user.user_files = file_path
        db.session.add(current_user)
        db.session.commit()

        with open(file_path) as f:
            file_content = f.read()

        return file_content
    else:
        result = request.args.get['myfile']
    return result


@cri.route('/v1.0')
def cri_chart():
    author_id = current_user.id
    file_path = User_files.query.filter_by(author_id=author_id).all()
    with open(file_path) as f:
        data = pd.read_csv(f, sep=" ", header=None)

    if len(data) is 0:
        flash('No spectrum is uploaded!')

    line = Line(title="CRI", width=800, height=400)

    attr = data.ix[:, [0]]
    d = data.ix[:, [1]]
    line.add("Spectrum", attr, d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
             mark_point=["min", "max"])
    line.render(r"../templates/cri_render.html")

    return render_template('cri_chart.html')

