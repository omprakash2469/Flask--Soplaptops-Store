# ------- Environment -------
development = False

if development:
    # --------------- Development Config ---------------
    class Config(object):
        DEBUG = True
        DEVELOPMENT = True
        SECRET_KEY = "This is my secret key"
        # SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/soplaptops"
        SQLALCHEMY_DATABASE_URI = "sqlite:///soplaptops.db"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
else:
    # --------------- Production Config ---------------
    class Config(object):
        DEBUG = False
        DEVELOPMENT = False
        SECRET_KEY = "afijoi23jooHOIFOEIKJLDFJLSDJFaoefhaognowe2342523413joijfao2342"
        SQLALCHEMY_DATABASE_URI = "sqlite:///soplaptops.db"
        SQLALCHEMY_TRACK_MODIFICATIONS = False