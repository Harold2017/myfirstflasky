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
        valid = 0

        if form.validate_on_submit():
            options = form.sensor.data
            line = Line(title='LineChart', width=800, height=400)
            for sensor in options:
                sensor_data = Sensor_data.query.filter_by(sensor_id=sensor).order_by(-Sensor_data.id.desc()).all()
                timestamp = []
                data = []
                for i in sensor_data:
                    timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
                    data.append(i.value)
                if len(data) is 0:
                    no_sensor = 0
                    return render_template('no_sensor_dat.html', no_sensor=no_sensor)
                else:
                    s = Sensors.query.filter_by(id=sensor).first()
                    title = s.name
                    attr = timestamp
                    d = data
                    line.add(title, attr, d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
                             mark_point=["min", "max"])
            valid = 1
            return render_template('sensor_chart.html', form=form, chart=line.render_embed(), valid=valid)
        else:
            valid = 0
        return render_template('sensor_chart.html', form=form, valid=valid)
    else:
        no_sensor = 1
        return render_template('no_sensor_dat.html', no_sensor=no_sensor)

    #if request.method == 'POST':
        #options = request.form.getlist('myform')
        #as_dict = request.form.to_dict()
        #print(request)
        #print(options)


