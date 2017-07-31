from flask import render_template, flash
from flask_login import login_required, current_user
from .. models import User, Api
from . import chart
from pytz import timezone
#import pygal
from pyecharts import Line

tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')

@chart.route('/v1.0')
@login_required

def chart():
	author_id = current_user.id
	api = Api.query.filter_by(author_id = author_id).all()
	timestamp = []
	data = []
	for i in api:
		timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
		data.append(i.value)
	if len(data) is 0:
		flash('No data is recorded!')
	
	#line_chart = pygal.Line()
	#line_chart.title = 'Data VS. Time'
	#line_chart.x_labels = timestamp
	#line_chart.add('Data', data)
	line = Line(title="Data VS. Time", width=800, height=400)
	attr = timestamp
	d = data
	line.add("data", attr, d, is_smooth=False, is_datazoom_show=True, mark_line = ["average"],
			 mark_point = ["min", "max"])
	line.render(r"/home/pi/myproject/flasky/app/templates/render.html")


	return render_template('echart.html')
