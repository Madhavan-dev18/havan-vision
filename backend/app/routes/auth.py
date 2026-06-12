"""Authentication routes — register, login, refresh, profile."""

import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,      
    set_refresh_cookies,     
    unset_jwt_cookies        
)
from app import db, bcrypt
from app.models import User

auth_bp = Blueprint("auth", __name__)

# ── Utility route to wipe stale/corrupted cookies ─────────────────────────
@auth_bp.get("/clear")
def clear_cookies():
    response = jsonify({"msg": "All stale cookies destroyed."})
    unset_jwt_cookies(response)
    return response

@auth_bp.post("/register")
def register():
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip().lower()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        display_name = (data.get("display_name") or username).strip()

        if not username or not email or not password:
            return jsonify({"error": "username, email, and password are required"}), 400

        if len(username) < 3 or len(username) > 32:
            return jsonify({"error": "Username must be 3–32 characters"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        # Check for duplicates
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            username=username,
            email=email,
            password_hash=pw_hash,
            display_name=display_name,
        )
        db.session.add(user)
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Attach tokens to HTTPOnly cookies
        response = jsonify({"user": user.to_public_dict()})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        return response, 201

    except Exception as e:
        db.session.rollback()
        # Log the actual error to your Render dashboard
        print(f"CRITICAL REGISTER ERROR: {str(e)}") 
        return jsonify({"error": "Registration failed due to a database error."}), 500


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "credentials required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    user.last_seen = datetime.now(timezone.utc)
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Attach tokens to HTTPOnly cookies
    response = jsonify({"user": user.to_public_dict()})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    
    return response


@auth_bp.post("/logout")
def logout():
    # Destroy the cookies server-side
    response = jsonify({"msg": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    response = jsonify({"msg": "Token refreshed"})
    set_access_cookies(response, access_token)
    return response


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_public_dict()})


@auth_bp.patch("/me")
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    if "display_name" in data:
        user.display_name = data["display_name"].strip()[:100]
    if "avatar_emoji" in data:
        user.avatar_emoji = data["avatar_emoji"][:8]
    if "preferences" in data and isinstance(data["preferences"], dict):
        user.preferences = json.dumps(data["preferences"])

    db.session.commit()
    return jsonify({"user": user.to_public_dict()})