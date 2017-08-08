from flask import render_template, flash
from flask_login import login_required, current_user
from ..models import Api, Sensors, Sensor_data
from . import chart
from pytz import timezone
# import pygal
from pyecharts import Line
import os

tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')


@chart.route('/v1.0')
@login_required
def chart1():
    author_id = current_user.id
    api = Api.query.filter_by(author_id=author_id).all()
    timestamp = []
    data = []
    for i in api:
        timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
        data.append(i.value)
    if len(data) is 0:
        flash('No data is recorded!')
        valid = 0
    else:

        # line_chart = pygal.Line()
        # line_chart.title = 'Data VS. Time'
        # line_chart.x_labels = timestamp
        # line_chart.add('Data', data)
        line = Line(title="Data VS. Time", width=800, height=400)
        attr = timestamp
        d = data
        line.add("data", attr, d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
                 mark_point=["min", "max"])
        path = os.path.abspath("app/templates") + "\\render.html"
        line.render(path)
        valid = 1

    return render_template('echart.html', valid=valid)


@chart.route('/v2.0/<sensor>')
@login_required
def chart2(sensor):
    sensor_data = Sensor_data.query.filter_by(sensor_id=sensor).order_by(Sensor_data.id.desc()).all()
    timestamp = []
    data = []
    for i in sensor_data:
        timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
        data.append(i.value)
    if len(data) is 0:
        flash('No data is recorded!')
        valid = 0
    else:
        s = Sensors.query.filter_by(id=sensor).first()
        title = s.name
        line = Line(title=title, width=800, height=400)
        attr = timestamp
        d = data
        line.add("data", attr, d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
                 mark_point=["min", "max"])
        path = os.path.abspath("app/templates") + "\\sensor_render.html"
        line.render(path)
        valid = 1

    return render_template('sensor_chart.html', valid=valid)
