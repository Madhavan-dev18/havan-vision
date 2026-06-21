"""Tests for the LLM service — crisis interceptor and fallback logic."""
from app.services.llm_service import generate_response, _rule_based_fallback


class TestCrisisInterceptor:
    def test_crisis_interceptor_triggers(self):
        emotion_data = {
            "primary_emotion": "sadness",
            "sentiment": "negative",
            "is_crisis": True,
            "visual_emotion": "neutral",
        }
        result = generate_response(
            user_message="I want to end my life",
            emotion_data=emotion_data,
            conversation_history=[],
            groq_api_key="any_key",
            groq_model="llama-3.1-8b-instant",
        )
        assert result["source"] == "safety_interceptor"
        assert "988" in result["content"]  # Contains crisis hotline number

    def test_crisis_interceptor_ignores_normal(self):
        emotion_data = {
            "primary_emotion": "joy",
            "sentiment": "positive",
            "is_crisis": False,
            "visual_emotion": "happy",
        }
        # Without a valid API key, should fall back to rule-based (not crisis)
        result = generate_response(
            user_message="I am happy today",
            emotion_data=emotion_data,
            conversation_history=[],
            groq_api_key="",
            groq_model="llama-3.1-8b-instant",
        )
        assert result["source"] == "rule_fallback"


class TestRuleFallback:
    def test_fallback_no_api_key(self):
        emotion_data = {
            "primary_emotion": "neutral",
            "sentiment": "neutral",
            "is_crisis": False,
            "visual_emotion": "neutral",
        }
        result = generate_response(
            user_message="Hello",
            emotion_data=emotion_data,
            conversation_history=[],
            groq_api_key="",
            groq_model="llama-3.1-8b-instant",
        )
        assert result["source"] == "rule_fallback"
        assert len(result["content"]) > 0

    def test_fallback_sadness_negative(self):
        emotion_data = {"primary_emotion": "sadness", "sentiment": "negative"}
        result = _rule_based_fallback(emotion_data)
        assert result["source"] == "rule_fallback"
        assert "difficult" in result["content"].lower()

    def test_fallback_anger_negative(self):
        emotion_data = {"primary_emotion": "anger", "sentiment": "negative"}
        result = _rule_based_fallback(emotion_data)
        assert "frustrated" in result["content"].lower() or "angry" in result["content"].lower()

    def test_fallback_joy_positive(self):
        emotion_data = {"primary_emotion": "joy", "sentiment": "positive"}
        result = _rule_based_fallback(emotion_data)
        assert "wonderful" in result["content"].lower() or "happiness" in result["content"].lower()

    def test_fallback_unknown_combination(self):
        emotion_data = {"primary_emotion": "disgust", "sentiment": "negative"}
        result = _rule_based_fallback(emotion_data)
        # Falls through to default response
        assert result["source"] == "rule_fallback"
        assert len(result["content"]) > 0

    def test_fallback_missing_keys(self):
        """Ensure fallback handles missing keys gracefully."""
        result = _rule_based_fallback({})
        assert result["source"] == "rule_fallback"
        assert len(result["content"]) > 0
