import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-fallback-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///moodlens.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    MAX_MEMORY_TURNS = int(os.getenv("MAX_MEMORY_TURNS", 10))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-super-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_COOKIE_PATH = '/api/'
    JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'

    # ENABLED: Protects against Cross-Site Request Forgery
    JWT_COOKIE_CSRF_PROTECT = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

    # Supabase pooler (port 6543) runs PgBouncer in transaction mode.
    # - sslmode=require: Supabase requires SSL on all external connections.
    # - statement_cache_size=0: disables psycopg's server-side prepared
    #   statement cache, which transaction-mode PgBouncer does not support
    #   reliably across pooled connections.
    # - pool_size/max_overflow kept small to stay under Supabase's pooler
    #   connection limit (free tier ~15 total pooled connections).
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 0,
        "connect_args": {
            "sslmode": "require",
            "options": "-c statement_cache_size=0",
        },
    }


config_map = {"development": DevelopmentConfig, "production": ProductionConfig, "default": DevelopmentConfig}