class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = "This is my secret key"
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/soplaptops"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
