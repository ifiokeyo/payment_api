import os
from os.path import abspath, split, dirname

from dotenv import load_dotenv


dotenv_path = split(abspath(__file__))[0].replace('app', '.env')
load_dotenv(dotenv_path)


class Config(object):
    BASE_DIR = dirname(__file__)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfiguration(Config):
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfiguration(Config):
    TESTING = True
    DEBUG = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@db/test_salamantex"


app_configuration = {
    'production': Config,
    'development': DevelopmentConfiguration,
    'testing': TestingConfiguration
}
