from flask import Blueprint

mqtt = Blueprint('mqtt', __name__)

from .import views
