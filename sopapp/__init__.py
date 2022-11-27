# ----------- Flask Modules ----------- #
from flask import Flask, render_template
from werkzeug.security import generate_password_hash

# ----------- Application Modules ----------- #
from .models.auth import Admin, AdminRole
from .config import Config, production
from .extensions import db, login_manager, migration, ckeditor
from .functions import func_dict


# ----------- Register Extensions ----------- #
def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migration.init_app(app, db)
    ckeditor.init_app(app)

# ----------- Register Blueprints ----------- #
def register_blueprints(app):
    # Import Blueprints
    from .routes.main import main
    from .routes.auth import auth
    from .routes.users import users
    from .routes.admin import admin

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(admin)

# ----------- Database Configuration ----------- #
def configure_database(app):
    @app.before_first_request
    def initialize_database():
        # Create all tables
        db.create_all()
        create_user()
    
    def create_user():
        exist = Admin.query.count()
        if exist == 0:
            # Add Default User
            adduser = Admin(name='admin', email='development1270@gmail.com', password=generate_password_hash('development#website123', method="sha256"))
            db.session.add(adduser)
            db.session.commit()
            db.session.flush
            aid = adduser.id

            # Add Default Admin User
            roles = AdminRole(admin_id=aid, role_id=1)
            db.session.add(roles)
            db.session.commit()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


# ----------- Context Processors and Error Handlers ----------- #
def apply_themes(app):
    ## Error Handling
    # Invalid URL Error Handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    # Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', error=e), 500

    ## Jinja Function
    @app.context_processor
    def context_processor():
        return dict(authAdminRole=func_dict['authAdminRole'], getCategoryById=func_dict['getCategoryById'], roleIdByAdminId=func_dict['roleIdByAdminId'], NumberOfProducts=func_dict['NumberOfProducts'], roleByAdminId=func_dict['roleByAdminId'], returnSum=func_dict['returnSum'], getProductImages=func_dict['getProductImages'], production=production)


# ----------- Initialize the core application ----------- #
def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config())

    with app.app_context():
        register_extensions(app)
        register_blueprints(app)
        apply_themes(app)
        configure_database(app)

        return app