"""Tests for chat routes — sessions and message handling."""


class TestSessions:
    def test_create_session(self, client, auth_headers):
        res = client.post("/api/chat/sessions", json={
            "title": "Test conversation",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data["session"]["title"] == "Test conversation"

    def test_list_sessions_empty(self, client, auth_headers):
        res = client.get("/api/chat/sessions", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["sessions"] == []

    def test_list_sessions(self, client, auth_headers):
        client.post("/api/chat/sessions", json={"title": "S1"}, headers=auth_headers)
        client.post("/api/chat/sessions", json={"title": "S2"}, headers=auth_headers)
        res = client.get("/api/chat/sessions", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.get_json()["sessions"]) == 2

    def test_get_session(self, client, auth_headers):
        create_res = client.post("/api/chat/sessions", json={"title": "Detail"}, headers=auth_headers)
        session_id = create_res.get_json()["session"]["id"]
        res = client.get(f"/api/chat/sessions/{session_id}", headers=auth_headers)
        assert res.status_code == 200
        assert "messages" in res.get_json()

    def test_get_session_not_found(self, client, auth_headers):
        res = client.get("/api/chat/sessions/9999", headers=auth_headers)
        assert res.status_code == 404

    def test_delete_session(self, client, auth_headers):
        create_res = client.post("/api/chat/sessions", json={"title": "ToDelete"}, headers=auth_headers)
        session_id = create_res.get_json()["session"]["id"]
        del_res = client.delete(f"/api/chat/sessions/{session_id}", headers=auth_headers)
        assert del_res.status_code == 200
        # Archived sessions don't appear in list
        list_res = client.get("/api/chat/sessions", headers=auth_headers)
        assert len(list_res.get_json()["sessions"]) == 0

    def test_delete_session_not_found(self, client, auth_headers):
        res = client.delete("/api/chat/sessions/9999", headers=auth_headers)
        assert res.status_code == 404


class TestMessages:
    def _create_session(self, client, auth_headers):
        res = client.post("/api/chat/sessions", json={"title": "Chat"}, headers=auth_headers)
        return res.get_json()["session"]["id"]

    def test_send_message(self, client, auth_headers):
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "Hello, I'm feeling great today!",
            "visual_emotion": "happy",
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert "user_message" in data
        assert "assistant_message" in data
        assert "emotion" in data
        assert data["user_message"]["role"] == "user"
        assert data["assistant_message"]["role"] == "assistant"

    def test_send_message_empty(self, client, auth_headers):
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_send_message_too_long(self, client, auth_headers):
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "x" * 1501,
        }, headers=auth_headers)
        assert res.status_code == 413

    def test_send_message_auto_creates_title(self, client, auth_headers):
        sid = self._create_session(client, auth_headers)
        client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "This is my first message in the conversation",
        }, headers=auth_headers)
        # Verify the session title was updated
        session_res = client.get(f"/api/chat/sessions/{sid}", headers=auth_headers)
        title = session_res.get_json()["session"]["title"]
        assert "This is my first message" in title

    def test_send_message_invalid_visual_emotion(self, client, auth_headers):
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "Testing invalid emotion",
            "visual_emotion": "INVALID_EMOTION",
        }, headers=auth_headers)
        # Should succeed — invalid emotion falls back to neutral
        assert res.status_code == 200

    def test_send_message_to_nonexistent_session(self, client, auth_headers):
        res = client.post("/api/chat/sessions/9999/messages", json={
            "content": "Hello",
        }, headers=auth_headers)
        assert res.status_code == 404

    def test_unauthenticated_access(self, client):
        res = client.get("/api/chat/sessions")
        assert res.status_code == 401

    def test_send_message_with_joy_emotion(self, client, auth_headers):
        """Verify that 'joy' is accepted as a valid visual emotion (bug #7 fix)."""
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "I am so happy!",
            "visual_emotion": "joy",
        }, headers=auth_headers)
        assert res.status_code == 200

    def test_send_message_with_disgust_emotion(self, client, auth_headers):
        """Verify that 'disgust' is accepted as a valid visual emotion (bug #9 fix)."""
        sid = self._create_session(client, auth_headers)
        res = client.post(f"/api/chat/sessions/{sid}/messages", json={
            "content": "That was terrible",
            "visual_emotion": "disgust",
        }, headers=auth_headers)
        assert res.status_code == 200
