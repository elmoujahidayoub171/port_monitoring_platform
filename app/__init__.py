from flask import Flask


def create_app():
    """
    Application factory.
    """

    app = Flask(
        __name__,
        template_folder="../dashboard/templates",
        static_folder="../dashboard/static",
        static_url_path="/static",
    )

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    app.config["SECRET_KEY"] = "development-secret-key"

    # ---------------------------------------------------------
    # Register blueprints
    # ---------------------------------------------------------

    from app.blueprints.dashboard.routes import dashboard_bp

    app.register_blueprint(dashboard_bp , url_prefix='/')

    return app