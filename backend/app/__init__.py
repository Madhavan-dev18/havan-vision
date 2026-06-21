"""
Havan Vision — Emotion-Aware AI Chat
Flask application factory.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os
import re

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "60 per hour"])

def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    # ── Proxy Fix for Rate Limiting ──────────────────────────────────────
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    from app.config import config_map
    app.config.from_object(config_map[config_name])

    # ── Extensions ───────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # ── CORS CONFIGURATION ────────────────────────────────────────────────
    # Explicit origins from env (comma-separated) — covers custom domains,
    # localhost dev, and your stable Vercel production alias.
    origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

    # Every Vercel deployment (preview AND "production") gets its own unique
    # *.vercel.app URL, e.g. https://havan-a-emotion-aware-chat-assistant-XXXXXXXXX.vercel.app
    # New URLs are generated on every push, so an exact-match allowlist breaks
    # on each deploy. This regex allows any subdomain of vercel.app belonging
    # to this project, in addition to the explicit origins above.
    vercel_origin_regex = r"^https://havan-vision[\w-]*\.vercel\.app$"

    # supports_credentials=True is REMOVED. Headers are allowed for JWT Bearer auth.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins + [re.compile(vercel_origin_regex)],
            }
        },
        allow_headers=["Content-Type", "Authorization"],
    )

    # ── Logging ──────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    return app