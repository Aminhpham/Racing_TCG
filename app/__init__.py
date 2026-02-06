from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Extensions (initialized here, used everywhere)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"   # redirect for @login_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.portal import portal_bp
    from app.routes.decks import decks_bp
    from app.routes.cards import cards_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(decks_bp)
    app.register_blueprint(cards_bp)

    return app
