from .. models import User, Api, Api_gps
from .. import db
from . import api
from flask import request, jsonify
from datetime import datetime
from pytz import timezone
tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')

@api.route('/v1.0/<token>', methods=['GET'])
def verify_token_get1(token):
    if token is None:
        return "No valid Token", 404
    user = User.query.filter_by(api_hash = token).first()
    api = Api.query.filter_by(author_id = user.id).order_by(Api.id.desc()).first()
    t = api.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')
    v = api.value
    return jsonify(t, v), 201


@api.route('/v1.0/<token>/<option>', methods=['GET'])
def verify_token_get(token, option):
    if token is None:
        return "No Valid Token", 404
    user = User.query.filter_by(api_hash = token).first()
    if option == 'all':
        api = Api.query.filter_by(author_id = user.id).all()
    else:
        api = Api.query.filter_by(author_id = user.id).order_by(Api.id.desc()).limit(option).all()
    t = []
    v = []
    data = {}
    for i in api:
        t.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
        v.append(i.value)
    data = dict(zip(t,v))
    return jsonify(data), 201

@api.route('/v1.0/<token>', methods=['POST'])
def verify_token_post(token):
    if token is None:
        return "No Valid Token", 404
    r = request.get_json(force=True)
    if r is None:
        return "No Data Posted", 405
    timestamp = r['timestamp']
    if str(timestamp) ==  'None':
        timestamp = datetime.utcnow()
    value = r['value']
    user = User.query.filter_by(api_hash = token).first()
    #api = Api.query.filter_by(user_id = user.id).first()
    api_n =Api(author_id=user.id)
    api_n.timestamp = timestamp
    api_n.value = value
    db.session.add(api_n)
    db.session.commit()
    return "Uploaded", 201

@api.route('/v1.0/gps/<token>', methods=['POST'])
def verify_gps_post(token):
	if token is None:
		return "No Valid Token", 404
	r = request.get_json(force=True)
	if r is None:
		return "No Data Posted", 405
	timestamp = r['timestamp']
	if str(timestamp) == 'None':
		timestamp = datetime.utcnow()
	lat = r['lat']
	lng = r['lng']
	user = User.query.filter_by(api_hash = token).first()
	gps_n = Api_gps(author_id=user.id)
	gps_n.timestamp = timestamp
	gps_n.lat = lat
	gps_n.lng = lng
	db.session.add(gps_n)
	db.session.commit()
	return "Uploaded", 201
