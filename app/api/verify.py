from ..models import User, Api, Api_gps, Sensor_data, Sensors
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
        return "No valid Token", 401
    user = User.query.filter_by(api_hash=token).first()
    api = Api.query.filter_by(author_id=user.id).order_by(Api.id.desc()).first_or_404()
    t = api.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')
    v = api.value
    return jsonify(t, v), 200


@api.route('/v1.0/<token>/<option>', methods=['GET'])
def verify_token_get(token, option):
    if token is None:
        return "No Valid Token", 401
    user = User.query.filter_by(api_hash=token).first()
    api = Api.query.filter_by(author_id=user.id).first_or_404()
    if option == 'all':
        api = Api.query.filter_by(author_id=user.id).all()
    else:
        api = Api.query.filter_by(author_id=user.id).order_by(Api.id.desc()).limit(option).all()
    t = []
    v = []
    data = {}
    for i in api:
        t.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
        v.append(i.value)
    data = dict(zip(t, v))
    return jsonify(data), 200


@api.route('/v1.0/<token>', methods=['POST'])
def verify_token_post(token):
    if token is None:
        return "No Valid Token", 401
    r = request.get_json(force=True)
    if r is None:
        return "No Data Posted", 400
    timestamp = r['timestamp']
    if str(timestamp) == 'None':
        timestamp = datetime.utcnow()
    value = r['value']
    user = User.query.filter_by(api_hash=token).first()
    # api = Api.query.filter_by(user_id = user.id).first()
    api_n = Api(author_id=user.id)
    api_n.timestamp = timestamp
    api_n.value = value
    db.session.add(api_n)
    db.session.commit()
    return "Uploaded", 201


@api.route('/v1.0/gps/<token>', methods=['POST'])
def verify_gps_post(token):
    if token is None:
        return "No Valid Token", 401
    r = request.get_json(force=True)
    if r is None:
        return "No Data Posted", 400
    timestamp = r['timestamp']
    if str(timestamp) == 'None':
        timestamp = datetime.utcnow()
    lat = r['lat']
    lng = r['lng']
    user = User.query.filter_by(api_hash=token).first()
    gps_n = Api_gps(author_id=user.id)
    gps_n.timestamp = timestamp
    gps_n.lat = lat
    gps_n.lng = lng
    db.session.add(gps_n)
    db.session.commit()
    return "Uploaded", 201


@api.route('/v2.0/<token>/<sensor_id>', methods=['GET'])
def verify_token_get2(sensor_id, token):
    if token is None:
        return "No valid Token", 401
    user = User.query.filter_by(api_hash=token).first()
    sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
    s = []
    for sensor in sensors:
        s.append(sensor.id)
    if int(sensor_id) not in s:
        return "Sensor not registered", 404
    sensor_data = Sensor_data.query.filter_by(sensor_id=sensor_id).order_by(Sensor_data.id.desc()).first_or_404()
    if sensor_data.value is None:
        return "No data stored", 404
    t = sensor_data.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')
    v = sensor_data.value
    return jsonify(t, v), 200


@api.route('/v2.0/<token>/<sensor_id>/<option>', methods=['GET'])
def verify_token_get21(sensor_id, token, option):
    if token is None:
        return "No Valid Token", 401
    user = User.query.filter_by(api_hash=token).first()
    sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
    s = []
    for sensor in sensors:
        s.append(sensor.id)
    if int(sensor_id) not in s:
        return "Sensor not registered", 404
    if option == 'all':
        sensor_data = Sensor_data.query.filter_by(sensor_id=sensor_id).order_by(Sensor_data.id.desc()).all()
    else:
        sensor_data = Sensor_data.query.filter_by(sensor_id=sensor_id). \
            order_by(Sensor_data.id.desc()).limit(option).all()
    t = []
    v = []
    for i in sensor_data:
        t.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
        v.append(i.value)
    data = dict(zip(t, v))
    return jsonify(data), 200


@api.route('/v2.0/<token>/<sensor_id>', methods=['POST'])
def verify_token_post2(sensor_id, token):
    if token is None:
        return "No Valid Token", 401
    r = request.get_json(force=True)
    if r is None:
        return "No Data Posted", 400
    timestamp = r['timestamp']
    if str(timestamp) == 'None':
        timestamp = datetime.utcnow()
    value = r['value']
    user = User.query.filter_by(api_hash=token).first()
    sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
    s = []
    for sensor in sensors:
        s.append(sensor.id)
    if int(sensor_id) not in s:
        return "Sensor not registered", 404
    sensor_data = Sensor_data(sensor_id=sensor_id)
    sensor_data.timestamp = timestamp
    sensor_data.value = value
    db.session.add(sensor_data)
    db.session.commit()
    return "Uploaded", 201
