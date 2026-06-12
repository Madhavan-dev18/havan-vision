from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix  # ADD THIS
import logging
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "60 per hour"])

def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    
    # ── Proxy Fix for Rate Limiting ──────────────────────────────────────
    # Tells Flask to trust the X-Forwarded-For headers from your reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    from app.config import config_map
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    # DELETED: with app.app_context(): db.create_all()
    # Run `flask db upgrade` in your deployment pipeline instead.

    return app