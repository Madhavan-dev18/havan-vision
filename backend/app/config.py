"""
Configuration classes for MoodLens backend.
Uses environment variables; falls back to safe dev defaults.
"""

import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod-abc123")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # HuggingFace model names — no API key required for inference on free tier
    EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
    SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")
    # Groq free tier LLM (set GROQ_API_KEY in .env; free 14k req/day)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    # Fallback: rule-based responses when no API key set
    USE_LOCAL_RESPONSES = os.getenv("USE_LOCAL_RESPONSES", "true").lower() == "true"
    MAX_MEMORY_TURNS = int(os.getenv("MAX_MEMORY_TURNS", "10"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///moodlens_dev.db")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///moodlens_prod.db"
    ).replace("postgres://", "postgresql://")  # Render/Railway compat


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=30)


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}