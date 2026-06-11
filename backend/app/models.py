"""
SQLAlchemy models for MoodLens.

Tables:
    User                — account + profile
    ConversationSession — groups messages per session
    Message             — individual chat turns with emotion metadata
    JournalEntry        — mood journal records
"""

from datetime import datetime, timezone
import uuid
from app import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(100))
    avatar_emoji = db.Column(db.String(8), default="🧠")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    last_seen = db.Column(db.DateTime(timezone=True), default=utcnow)
    preferences = db.Column(db.Text, default="{}")

    sessions = db.relationship("ConversationSession", back_populates="user", cascade="all, delete-orphan")
    journal_entries = db.relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")

    def to_public_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name or self.username,
            "avatar_emoji": self.avatar_emoji,
            "created_at": self.created_at.isoformat(),
        }


class ConversationSession(db.Model):
    __tablename__ = "conversation_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), default="New conversation")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    dominant_emotion = db.Column(db.String(32))
    message_count = db.Column(db.Integer, default=0)
    is_archived = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="sessions")
    messages = db.relationship("Message", back_populates="session", cascade="all, delete-orphan",
                               order_by="Message.created_at")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "dominant_emotion": self.dominant_emotion,
            "message_count": self.message_count,
        }


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    role = db.Column(db.String(16), nullable=False)  # "user" | "assistant"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    # Emotion payload (only for user messages)
    primary_emotion = db.Column(db.String(32))
    visual_emotion = db.Column(db.String(32), default="neutral") # The new visual data column
    emotion_scores = db.Column(db.Text)  # JSON blob: {"joy": 0.8, "sadness": 0.1, ...}
    sentiment = db.Column(db.String(16))  # positive | negative | neutral
    sentiment_score = db.Column(db.Float)
    intensity = db.Column(db.Float)  # 0-1 composite intensity

    session = db.relationship("ConversationSession", back_populates="messages")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "emotion": {
                "primary": self.primary_emotion,
                "visual": self.visual_emotion,
                "scores": json.loads(self.emotion_scores) if self.emotion_scores else {},
                "sentiment": self.sentiment,
                "sentiment_score": self.sentiment_score,
                "intensity": self.intensity,
            } if self.primary_emotion else None,
        }


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    mood_tag = db.Column(db.String(32))
    emotion_data = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    word_count = db.Column(db.Integer, default=0)

    user = db.relationship("User", back_populates="journal_entries")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "content": self.content,
            "mood_tag": self.mood_tag,
            "emotion_data": json.loads(self.emotion_data) if self.emotion_data else {},
            "created_at": self.created_at.isoformat(),
            "word_count": self.word_count,
        }