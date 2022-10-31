# --------------- Development Config ---------------
class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = "This is my secret key"
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/soplaptops"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# --------------- Production Config ---------------
# class Config(object):
#     DEBUG = False
#     DEVELOPMENT = False
#     SECRET_KEY = "this-is-my-super-secret-key"
#     SQLALCHEMY_DATABASE_URI = "sqlite:///soplaptops.db"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
