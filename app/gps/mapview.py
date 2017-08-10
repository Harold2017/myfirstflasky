from ..models import User, Api_gps
from . import gps
from flask import render_template, current_app, flash
from flask_login import login_required, current_user
from pytz import timezone
from flask_googlemaps import Map, icons

tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')


@gps.route('/v1.0')
@login_required
def mapview():
    author_id = current_user.id
    api_gps = Api_gps.query.filter_by(author_id=author_id).order_by(Api_gps.id.desc()).all()
    lat = []
    lng = []
    path = []
    markers = []
    timestamp = []
    for i in api_gps:
        lat.append(i.lat)
        lng.append(i.lng)
        timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
    for i in range(len(lat)):
        path.append((lat[i], lng[i]))
        markers.append({'icon': icons.dots.blue, 'lat': lat[i], 'lng': lng[i],
                        'infobox': timestamp[i]})

    if len(path) is 0:
        flash('No GPS data is recorded!')
        lat_d = 22.4274
        lng_d = 114.2111
    else:
        lat_d = lat[0]
        lng_d = lng[0]

    polyline = {
        'stroke_color': '#00AEAE',
        'stroke_opacity': 1.0,
        'stroke_weight': 3,
        'path': path,
    }

    plinemap = Map(
        identifier="plinemap",
        varname="plinemap",
        lat=lat_d,
        lng=lng_d,
        zoom=17,
        style="height:350px;width:350px;margin:0;",
        markers=markers,
        polylines=[polyline]
    )

    return render_template('gps.html', plinemap=plinemap)
