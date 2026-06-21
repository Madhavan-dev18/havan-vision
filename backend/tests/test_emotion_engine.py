"""Tests for the emotion analysis engine."""
from app.services.emotion_engine import analyze, get_emotion_trend, _empty_result


class TestAnalyze:
    def test_analyze_empty_string(self):
        result = analyze("")
        assert result["primary_emotion"] == "neutral"
        assert result["intensity"] == 0.0
        assert result["is_crisis"] is False

    def test_analyze_whitespace_only(self):
        result = analyze("   ")
        assert result["primary_emotion"] == "neutral"

    def test_analyze_happy_text(self):
        result = analyze("I am so happy and excited today! This is wonderful!")
        assert result["primary_emotion"] == "joy"
        assert result["sentiment"] == "positive"
        assert result["intensity"] > 0

    def test_analyze_sad_text(self):
        result = analyze("I feel so sad and miserable. I am crying and lonely.")
        assert result["primary_emotion"] == "sadness"
        assert result["sentiment"] == "negative"

    def test_analyze_angry_text(self):
        result = analyze("I am so angry and furious! I hate this stupid thing!")
        assert result["primary_emotion"] == "anger"
        assert result["sentiment"] == "negative"

    def test_analyze_neutral_text(self):
        result = analyze("The meeting is at three o'clock.")
        assert result["primary_emotion"] == "neutral"
        assert result["sentiment"] == "neutral"

    def test_analyze_fearful_text(self):
        result = analyze("I am so scared and terrified. I feel anxious and nervous.")
        assert result["primary_emotion"] == "fear"

    def test_analyze_surprised_text(self):
        result = analyze("Wow, I am so surprised and shocked! Unbelievable!")
        assert result["primary_emotion"] == "surprise"

    def test_crisis_detection(self):
        result = analyze("I want to kill myself")
        assert result["is_crisis"] is True

    def test_crisis_detection_no_reason_to_live(self):
        result = analyze("I feel like there is no reason to live")
        assert result["is_crisis"] is True

    def test_no_crisis_normal_text(self):
        result = analyze("I had a great day at work today!")
        assert result["is_crisis"] is False

    def test_result_has_required_fields(self):
        result = analyze("Hello world")
        required_keys = {
            "primary_emotion", "emotion_scores", "sentiment",
            "sentiment_score", "intensity", "is_crisis", "color", "emoji"
        }
        assert required_keys.issubset(set(result.keys()))

    def test_intensity_range(self):
        result = analyze("I am happy")
        assert 0.0 <= result["intensity"] <= 1.0

    def test_sentiment_score_range(self):
        result = analyze("I am happy")
        assert 0.0 <= result["sentiment_score"] <= 1.0


class TestEmptyResult:
    def test_empty_result_structure(self):
        result = _empty_result()
        assert result["primary_emotion"] == "neutral"
        assert result["emotion_scores"]["neutral"] == 1.0
        assert result["is_crisis"] is False


class TestEmotionTrend:
    def test_emotion_trend_empty(self):
        assert get_emotion_trend([]) == {}

    def test_emotion_trend_single(self):
        emotions = [analyze("I am happy")]
        trend = get_emotion_trend(emotions)
        assert "dominant_emotion" in trend
        assert trend["total_messages"] == 1

    def test_emotion_trend_multiple(self):
        emotions = [
            analyze("I am happy"),
            analyze("I am sad"),
            analyze("I am angry"),
        ]
        trend = get_emotion_trend(emotions)
        assert trend["total_messages"] == 3
        assert "emotion_distribution" in trend
        assert "avg_intensity" in trend
        assert trend["intensity_trend"] in ("rising", "falling", "stable")

    def test_emotion_trend_dominant(self):
        emotions = [
            analyze("I am so happy and excited!"),
            analyze("This is wonderful and great!"),
            analyze("I feel neutral about this"),
        ]
        trend = get_emotion_trend(emotions)
        assert trend["dominant_emotion"] in ("joy", "neutral")
