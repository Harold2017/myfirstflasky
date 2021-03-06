from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
from flask_googlemaps import GoogleMaps

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['UPLOAD_FOLDER'] = './uploads'
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    GoogleMaps(app, key="AIzaSyDOqdKlBwyAWZj8REdqLWpR3NDU4f2q8IE")

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .gps import gps as gps_blueprint
    app.register_blueprint(gps_blueprint, url_prefix='/gps')

    from .chart import chart as chart_blueprint
    app.register_blueprint(chart_blueprint, url_prefix='/chart')

    from .cri import cri as cri_blueprint
    app.register_blueprint(cri_blueprint, url_prefix='/cri')

    from .manual import manual as manual_blueprint
    app.register_blueprint(manual_blueprint, url_prefix='/manual')

    from .mqtt import mqtt as mqtt_blueprint
    app.register_blueprint(mqtt_blueprint, url_prefix='/mqtt')

    from .colour_science import colour_science as colour_science_blueprint
    app.register_blueprint(colour_science_blueprint, url_prefix='/colour_science')

    return app
