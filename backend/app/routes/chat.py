"""
Chat routes — session management + emotion-aware message handling.
"""

import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import ConversationSession, Message, User
from app.services import emotion_engine, llm_service

chat_bp = Blueprint("chat", __name__)


# ── Session endpoints ────────────────────────────────────────────────────────

@chat_bp.get("/sessions")
@jwt_required()
def list_sessions():
    user_id = get_jwt_identity()
    sessions = (
        ConversationSession.query
        .filter_by(user_id=user_id, is_archived=False)
        .order_by(ConversationSession.updated_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"sessions": [s.to_dict() for s in sessions]})


@chat_bp.post("/sessions")
@jwt_required()
def create_session():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "New conversation").strip()[:200]

    session = ConversationSession(user_id=user_id, title=title)
    db.session.add(session)
    db.session.commit()
    return jsonify({"session": session.to_dict()}), 201


@chat_bp.get("/sessions/<session_id>")
@jwt_required()
def get_session(session_id):
    user_id = get_jwt_identity()
    session = ConversationSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    messages = [m.to_dict() for m in session.messages]
    return jsonify({"session": session.to_dict(), "messages": messages})


@chat_bp.delete("/sessions/<session_id>")
@jwt_required()
def delete_session(session_id):
    user_id = get_jwt_identity()
    session = ConversationSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404
    session.is_archived = True
    db.session.commit()
    return jsonify({"ok": True})


# ── Message endpoint ─────────────────────────────────────────────────────────

@chat_bp.post("/sessions/<session_id>/messages")
@jwt_required()
def send_message(session_id):
    user_id = get_jwt_identity()
    session = ConversationSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    visual_emotion = data.get("visual_emotion", "neutral") # GET THE VISUAL DATA

    if not content:
        return jsonify({"error": "Message content required"}), 400

    # 1. Analyse textual emotion
    emotion_data = emotion_engine.analyze(content)
    # Inject visual emotion into the payload for the LLM
    emotion_data["visual_emotion"] = visual_emotion 

    # 2. Persist user message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=content,
        primary_emotion=emotion_data["primary_emotion"],
        visual_emotion=visual_emotion, # SAVE TO DATABASE
        emotion_scores=json.dumps(emotion_data["emotion_scores"]),
        sentiment=emotion_data["sentiment"],
        sentiment_score=emotion_data["sentiment_score"],
        intensity=emotion_data["intensity"],
    )
    db.session.add(user_msg)
    
    # ... keep the rest of the function the same ...

    # ── 3. Build conversation history for LLM context ───────────────────
    history = [
        {"role": m.role, "content": m.content}
        for m in session.messages[-current_app.config["MAX_MEMORY_TURNS"]:]
    ]

    # ── 4. Generate response ─────────────────────────────────────────────
    llm_result = llm_service.generate_response(
        user_message=content,
        emotion_data=emotion_data,
        conversation_history=history,
        groq_api_key=current_app.config.get("GROQ_API_KEY", ""),
        groq_model=current_app.config.get("GROQ_MODEL", "llama3-8b-8192"),
    )

    # ── 5. Persist assistant message ────────────────────────────────────
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=llm_result["content"],
    )
    db.session.add(assistant_msg)

    # ── 6. Update session metadata ───────────────────────────────────────
    session.message_count = (session.message_count or 0) + 2
    session.updated_at = datetime.now(timezone.utc)
    session.dominant_emotion = emotion_data["primary_emotion"]

    # Auto-title from first message
    if session.message_count <= 2:
        session.title = content[:60] + ("…" if len(content) > 60 else "")

    db.session.commit()

    return jsonify({
        "user_message": user_msg.to_dict(),
        "assistant_message": assistant_msg.to_dict(),
        "emotion": emotion_data,
        "response_source": llm_result["source"],
    })


# ── Quick emotion analysis (no session required) ─────────────────────────────

@chat_bp.post("/analyze")
@jwt_required()
def analyze_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    result = emotion_engine.analyze(text)
    return jsonify(result)