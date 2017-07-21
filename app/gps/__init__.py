from flask import Blueprint

gps = Blueprint('gps', __name__)

from . import mapview
