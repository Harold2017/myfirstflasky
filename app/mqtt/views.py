from . import mqtt
from pytz import timezone
from ..models import mqtt_data, mqtt_gps
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


@mqtt.route('/gps/<option>', methods=['GET'])
def gps(option):
    gps = mqtt_gps.query.filter_by(author_id=option).order_by(mqtt_gps.id.desc()).limit(200).all()
    data = []
    for i in gps:
        tmp = {"timestamp": i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S')}
        d = json.loads(i.message)
        dd = dict(d, **tmp)
        data.append(dd)
    return jsonify(data), 200


