# ----------- Flask Modules ----------- #
from flask import Flask, render_template
from flask_login import LoginManager

# ----------- Application Modules ----------- #
from .models.auth import Admin
from .config import Config
from .extensions import db, ckeditor
from .functions import func_dict

def create_app():
    # ----------- Initialize the core application ----------- #
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config())
    
    # ----------- Initialize Plugins ----------- #
    db.init_app(app)
    ckeditor.init_app(app)

    # ----------- Login Manager ----------- #
    login_manager = LoginManager()
    login_manager.login_view = 'auth.adminLogin'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # ----------- Error Handling ----------- #
    # Invalid URL Error Handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    # Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', error=e), 500

    # ----------- Jinja Function ----------- #
    @app.context_processor
    def context_processor():
        return dict(authAdminRole=func_dict['authAdminRole'], getCategoryById=func_dict['getCategoryById'], roleIdByAdminId=func_dict['roleIdByAdminId'], NumberOfProducts=func_dict['NumberOfProducts'], roleByAdminId=func_dict['roleByAdminId'], returnSum=func_dict['returnSum'])

    # ----------- Database Configuration ----------- #
    def configure_database(app):
        @app.before_first_request
        def initialize_database():
            db.create_all()

        @app.teardown_request
        def shutdown_session(exception=None):
            db.session.remove()
    

    # ----------- Set App Context ----------- #
    with app.app_context():
        # Import Our Routes
        from .routes.main import main
        from .routes.auth import auth
        from .routes.users import users
        from .routes.admin import admin

        # Register Blueprints
        app.register_blueprint(main)
        app.register_blueprint(auth)
        app.register_blueprint(users)
        app.register_blueprint(admin)

        # Database Configuration
        configure_database(app)
        return app