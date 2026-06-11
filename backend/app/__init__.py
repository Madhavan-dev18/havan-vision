"""
MoodLens — Emotion-Aware AI Chat
Flask application factory.
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "60 per hour"])


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    # ── Config ───────────────────────────────────────────────────────────
    from app.config import config_map
    app.config.from_object(config_map[config_name])

    # ── Extensions ───────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

    # ── Logging ──────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    #from app.routes.analytics import analytics_bp
    #from app.routes.journal import journal_bp
    #from app.routes.health import health_bp
    

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    #app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    #app.register_blueprint(journal_bp, url_prefix="/api/journal")
    #app.register_blueprint(health_bp, url_prefix="/api")

    # ── DB Bootstrap ─────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
    # app.register_blueprint(health_bp, url_prefix="/api")              <-- Commented out
    