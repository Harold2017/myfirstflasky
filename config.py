import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = 'Example'
    FLASKY_MAIL_SENDER = 'Example <example@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    #UPLOAD_FOLDER = basedir + '/uploads'
    #ALLOWED_EXTENSIONS = set(['csv', 'txt', 'png', 'jpg', 'jpeg'])
    #MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    RECAPTCHA_PUBLIC_KEY = '6LdIRz8UAAAAAJYJRrZuKDlRQTehaRE9uTcVsO9A'
    RECAPTCHA_PRIVATE_KEY = '6LdIRz8UAAAAAOjNSx8JsZtZtpdTMRyWelAvYSIY'
    # RECAPTCHA_PARAMETERS = {'hl': 'zh', 'render': 'explicit'}
    # RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}
    TESTING = False  # set app['TESTING'] to true for disabling reCaptcha

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              ('mysql://flasky:123456@127.0.0.1/flasky')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              ('mysql://flasky:123456@127.0.0.1/flasky')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              ('mysql://flasky:123456@127.0.0.1/flasky')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
