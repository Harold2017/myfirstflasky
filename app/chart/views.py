from flask import render_template, flash
from flask_login import login_required, current_user
from .. models import User, Api
from . import chart
from pytz import timezone
import pygal

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
	
	line_chart = pygal.Line()
	line_chart.title = 'Data VS. Time'
	line_chart.x_labels = timestamp
	line_chart.add('Data', data)

	return render_template('chart.html', chart=line_chart)
