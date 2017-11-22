from . import mqtt
from pytz import timezone
from ..models import mqtt_data, mqtt_gps, User
from flask import jsonify
import json


tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')


@mqtt.route('/v1.0', methods=['GET'])
def mqtt_d():
    mqtt = mqtt_data.query.filter_by().order_by(mqtt_data.id.desc()).limit(200).all()
    data = []
    for i in mqtt:
        tmp = {"timestamp": i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')}
        d = json.loads(i.message)
        dd = dict(d, **tmp)
        data.append(dd)

    return jsonify(data), 200


@mqtt.route('/gps/<token>/<option>', methods=['GET'])
def gps(token, option):
    if token is None:
        return "No Valid Token", 401
    user = User.query.filter_by(api_hash=token).first()
    if option:
        gps = []
        for i in range(1, int(option)+1):
            gps.append(mqtt_gps.query.filter_by(author_id=user.id, gps_id=i).first())
    else:
        gps = mqtt_gps.query.filter_by(author_id=user.id).order_by(mqtt_gps.id.desc()).all()
    data = []
    if (gps is None) or (len(gps) == 0):
        return 402
    for i in gps:
        tmp = {"timestamp": i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')}
        d = json.loads(i.message)
        dd = dict(d, **tmp)
        data.append(dd)
    return jsonify(data), 200


