"""
LLM Response Service for MoodLens.

Priority chain:
  1. Groq API (free tier, llama3-8b-8192) — 14,400 req/day
  2. HuggingFace Inference API (free tier, no key needed for small models)
  3. Rule-based empathetic responses (always available, zero dependencies)

This ensures the app works from day one with zero paid services.
"""

import os
import json
import logging
import random
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ── Static response library ──────────────────────────────────────────────────
# Fallback when no LLM is available. Keyed by (emotion, sentiment).
EMPATHETIC_RESPONSES = {
    ("joy", "positive"): [
        "That's wonderful to hear! Your joy is contagious. What's making you feel this way?",
        "I can feel the excitement in your words! Keep riding that wave — what's next for you?",
        "It's great seeing you in such a positive space. Tell me more about what's bringing this energy!",
    ],
    ("sadness", "negative"): [
        "I hear you, and I want you to know your feelings are completely valid. Would you like to talk about what's weighing on you?",
        "That sounds really hard. Sometimes just putting words to pain is the first step — I'm here to listen.",
        "It takes courage to share when you're hurting. Take your time — I'm not going anywhere.",
    ],
    ("anger", "negative"): [
        "It sounds like something really got under your skin. Want to walk me through what happened?",
        "That frustration makes sense given what you've described. Sometimes venting helps — I'm listening.",
        "I can feel the intensity here. What's the core of what's bothering you most?",
    ],
    ("fear", "negative"): [
        "What you're feeling is understandable — uncertainty can be really unsettling. What specifically is worrying you?",
        "Anxiety is exhausting, but you're not alone in this. Let's think through it together if that helps.",
        "Fear is often a signal, not a verdict. What does it feel like you're most afraid of right now?",
    ],
    ("surprise", "positive"): [
        "That sounds unexpected! Surprises can be disorienting — was this a good shock or not so much?",
        "Life has a way of throwing curveballs. How are you processing what just happened?",
    ],
    ("disgust", "negative"): [
        "That sounds genuinely unpleasant. Some things are just wrong — what happened?",
        "Your reaction makes complete sense. Moral disgust is a healthy signal. Want to unpack it?",
    ],
    ("neutral", "neutral"): [
        "I'm here and listening. What's on your mind today?",
        "Thanks for sharing. What would you like to explore or talk through?",
        "Tell me more — I want to understand where you're coming from.",
    ],
}

# Crisis safety response — always takes priority
CRISIS_RESPONSE = """I hear you, and I'm really glad you reached out. What you're feeling matters deeply.

**You are not alone.** Please consider reaching out to someone right now:

- 🇮🇳 **iCall (India):** 9152987821
- 🌐 **Vandrevala Foundation:** 1860-2662-345 (24/7)
- 💬 **iCall chat:** icallhelpline.org

I'm here to talk, but a trained counsellor can offer the support you deserve. Would you like to share more about what's going on?"""


def _get_fallback_response(emotion: str, sentiment: str) -> str:
    key = (emotion, sentiment)
    responses = EMPATHETIC_RESPONSES.get(key) or EMPATHETIC_RESPONSES.get(("neutral", "neutral"))
    return random.choice(responses)


def _build_system_prompt(emotion_data: dict, memory_summary: str) -> str:
    emotion = emotion_data.get("primary_emotion", "neutral")
    visual = emotion_data.get("visual_emotion", "neutral") # ADD THIS
    intensity = emotion_data.get("intensity", 0.5)
    sentiment = emotion_data.get("sentiment", "neutral")

    intensity_word = "strongly" if intensity > 0.7 else "moderately" if intensity > 0.4 else "mildly"

    return f"""You are MoodLens — an empathetic AI companion that responds with emotional intelligence.

Current emotional context:
- Textual Emotion: {intensity_word} feeling **{emotion}** ({sentiment} valence)
- Facial Expression: **{visual}**
- Intensity: {intensity:.0%}
# ... keep the rest of the prompt the same ...

Conversation memory:
{memory_summary or "No prior context."}

Your response guidelines:
1. Acknowledge the detected emotion naturally — don't say "I detected your emotion as X"
2. Be warm, non-judgmental, and genuinely curious
3. Ask ONE thoughtful follow-up question at the end
4. Keep response to 2-4 sentences unless the user needs more
5. Never give medical advice; if crisis signals appear, provide crisis resources
6. You are NOT a therapist — you are a supportive, emotionally intelligent companion
7. Adapt tone: energetic for joy, gentle for sadness, calm for anger, reassuring for fear"""


def _call_groq(
    messages: list[dict],
    system_prompt: str,
    api_key: str,
    model: str = "llama3-8b-8192",
) -> Optional[str]:
    """Call Groq's free-tier LLaMA3 API."""
    try:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning(f"Groq call failed: {exc}")
        return None


def _call_hf_inference(messages: list[dict], system_prompt: str) -> Optional[str]:
    """
    Call HuggingFace Inference API (free, no key needed for open models).
    Uses microsoft/DialoGPT-large — always free.
    """
    try:
        last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        resp = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
            headers={"Content-Type": "application/json"},
            json={"inputs": last_user_msg, "parameters": {"max_new_tokens": 150}},
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "").strip()
    except Exception as exc:
        logger.warning(f"HuggingFace Inference API failed: {exc}")
    return None


def generate_response(
    user_message: str,
    emotion_data: dict,
    conversation_history: list[dict],
    groq_api_key: str = "",
    groq_model: str = "llama3-8b-8192",
) -> dict:
    """
    Generate an empathetic response.

    Returns:
        {
          "content": str,
          "source": "groq" | "huggingface" | "local",
          "used_fallback": bool,
        }
    """
    # ── Crisis check ─────────────────────────────────────────────────────
    if emotion_data.get("is_crisis"):
        return {"content": CRISIS_RESPONSE, "source": "safety", "used_fallback": False}

    # ── Build memory summary (last N turns) ──────────────────────────────
    memory_turns = conversation_history[-10:]
    memory_summary = ""
    if memory_turns:
        lines = []
        for m in memory_turns:
            role_label = "User" if m["role"] == "user" else "MoodLens"
            lines.append(f"{role_label}: {m['content'][:120]}")
        memory_summary = "\n".join(lines)

    system_prompt = _build_system_prompt(emotion_data, memory_summary)

    # Build messages for LLM (last 6 turns to stay within token budget)
    llm_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in conversation_history[-6:]
    ]
    llm_messages.append({"role": "user", "content": user_message})

    # ── Priority 1: Groq ──────────────────────────────────────────────────
    if groq_api_key:
        response = _call_groq(llm_messages, system_prompt, groq_api_key, groq_model)
        if response:
            return {"content": response, "source": "groq", "used_fallback": False}

    # ── Priority 2: HuggingFace Inference API ────────────────────────────
    hf_response = _call_hf_inference(llm_messages, system_prompt)
    if hf_response and len(hf_response) > 20:
        return {"content": hf_response, "source": "huggingface", "used_fallback": False}

    # ── Priority 3: Rule-based empathetic library ────────────────────────
    emotion = emotion_data.get("primary_emotion", "neutral")
    sentiment = emotion_data.get("sentiment", "neutral")
    fallback = _get_fallback_response(emotion, sentiment)
    return {"content": fallback, "source": "local", "used_fallback": True}