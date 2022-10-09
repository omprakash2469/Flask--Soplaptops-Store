from flask import Flask, render_template
from .config import Config
from .extensions import db, ckeditor

def create_app():
    # Initialize the core application
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config())
    
    # Initialize Plugins
    db.init_app(app)
    ckeditor.init_app(app)

    # ----------- Error Handling ----------- #
    # Invalid URL Error Handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    # Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', error=e), 500

    with app.app_context():
        # Import Our Routes
        from .routes.main import main
        from .routes.users import users
        from .routes.admin import admin

        # Register Blueprints
        app.register_blueprint(main)
        app.register_blueprint(users)
        app.register_blueprint(admin)

        return app