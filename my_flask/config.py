import pathlib


class Config(object):
    SECRET_KEY = 'jsTHNwy6BBwWPrN3XwfvnA'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False


class ProductionConfig(Config):
    ENV = 'production'


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True

    DATA_PATH = pathlib.Path(__file__).parent.parent.joinpath("data")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(DATA_PATH.joinpath('my_flask.sqlite'))


class TestingConfig(Config):
    ENV = 'testing'
    DEBUG = True
    SQLALCHEMY_ECHO = True
