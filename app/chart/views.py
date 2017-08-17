from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import User, Sensors, Sensor_data
from . import chart
from pytz import timezone
# import pygal
from pyecharts import Line
import os
from ..main.forms import SelectMultipleSensorForm

tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')


@chart.route('/v1.0')
@login_required
def chart1():
    username = current_user.username
    return redirect(url_for('main.sensors', username=username))


@chart.route('/v2.0', methods=['GET', 'POST'])
@login_required
def chart3():
    if Sensors.query.filter_by(author_id=current_user.id).first():
        sensors = Sensors.query.filter_by(author_id=current_user.id).order_by(Sensors.id.desc()).all()
        form = SelectMultipleSensorForm(sensors, prefix="sensorform")
    if request.method == 'POST':
        options = request.form.getlist('myform')
        #as_dict = request.form.to_dict()
        #print(request)
        print(options)

    return render_template('sensor_chart.html', form=form)
