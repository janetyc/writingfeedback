import os

PROJECT_NAME = "feedback"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False

    #DATABASE CONFIGURATION
    #SQLALCHEMY_DATABASE_URI = "sqlite:///%s/%s.sqlite" % (BASE_DIR, PROJECT_NAME)
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/feedback"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///%s/%s.sqlite" % (BASE_DIR, PROJECT_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://localhost/feedback"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/feedback"
    #SQLALCHEMY_DATABASE_URI = "sqlite:///%s/%s.sqlite" % (BASE_DIR, PROJECT_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///%s/%s.sqlite" % (BASE_DIR, PROJECT_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://localhost/feedback"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class DebugConfig(Config):
    DEBUG = True
    TESTING = False
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///%s/%s.sqlite" % (BASE_DIR, PROJECT_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://localhost/feedback"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
