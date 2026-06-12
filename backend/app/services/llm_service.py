import os
import logging
import random
import requests
from typing import Optional

# Setup logging to show up in Render/Heroku logs
logger = logging.getLogger(__name__)

# Fallback library
EMPATHETIC_RESPONSES = {
    ("joy", "positive"): ["That's wonderful! What's making you feel this way?"],
    ("sadness", "negative"): ["I hear you. Do you want to talk about it?"],
    ("anger", "negative"): ["That sounds really frustrating. I'm listening."],
    ("neutral", "neutral"): ["I'm here. What's on your mind?"]
}

def _call_groq(messages: list[dict], system_prompt: str, api_key: str, model: str) -> Optional[str]:
    """Sends request to Groq with explicit error debugging."""
    if not api_key:
        logger.warning("LLM Service Warning: GROQ_API_KEY is empty. Using local fallback responses.")
        return None
    
    try:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Groq API returned {response.status_code}: {response.text}")
            return None
            
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"LLM Service Connection Failed: {str(e)}")
        return None

def generate_response(user_message, emotion_data, conversation_history, groq_api_key, groq_model):
    """
    Orchestrates the response. Fuses visual and text data if both are available.
    """
    primary_text_emotion = emotion_data.get('primary_emotion', 'neutral')
    visual_emotion = emotion_data.get('visual_emotion')
    
    # 1. Build the true context - Stop ignoring visual data
    if visual_emotion and visual_emotion != "neutral":
        system_prompt = f"You are an empathetic companion. The user's text emotion is {primary_text_emotion}, but their real-time facial expression shows {visual_emotion}. Address this combination appropriately."
    else:
        system_prompt = f"You are an empathetic companion. Current emotion: {primary_text_emotion}"
    
    # 2. Try the API
    llm_output = _call_groq(conversation_history[-6:], system_prompt, groq_api_key, groq_model)
    
    # 3. If API works, return it. If not, log the failure and return fallback.
    if llm_output:
        return {"content": llm_output, "source": "groq", "used_fallback": False}
    
    # Fallback
    fallback = random.choice(EMPATHETIC_RESPONSES.get(("neutral", "neutral"), ["..."]))
    return {"content": fallback, "source": "local", "used_fallback": True}