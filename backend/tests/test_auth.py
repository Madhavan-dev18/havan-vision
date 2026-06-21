"""Tests for authentication routes."""


class TestRegister:
    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
            "display_name": "New User",
        })
        assert res.status_code == 201
        data = res.get_json()
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "newuser"

    def test_register_duplicate_username(self, client):
        payload = {
            "username": "dupuser",
            "email": "dup1@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=payload)
        res = client.post("/api/auth/register", json={
            **payload,
            "email": "dup2@example.com",
        })
        assert res.status_code == 409
        assert "already taken" in res.get_json()["error"].lower()

    def test_register_duplicate_email(self, client):
        payload = {
            "username": "user1",
            "email": "same@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=payload)
        res = client.post("/api/auth/register", json={
            **payload,
            "username": "user2",
        })
        assert res.status_code == 409
        assert "already registered" in res.get_json()["error"].lower()

    def test_register_missing_fields(self, client):
        res = client.post("/api/auth/register", json={"username": "x"})
        assert res.status_code == 400

    def test_register_short_password(self, client):
        res = client.post("/api/auth/register", json={
            "username": "shortpw",
            "email": "short@example.com",
            "password": "1234567",  # 7 chars, minimum is 8
        })
        assert res.status_code == 400
        assert "8 characters" in res.get_json()["error"]

    def test_register_short_username(self, client):
        res = client.post("/api/auth/register", json={
            "username": "ab",  # 2 chars, minimum is 3
            "email": "short@example.com",
            "password": "password123",
        })
        assert res.status_code == 400

    def test_register_long_username(self, client):
        res = client.post("/api/auth/register", json={
            "username": "a" * 33,  # 33 chars, maximum is 32
            "email": "long@example.com",
            "password": "password123",
        })
        assert res.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        # Register first
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
        })
        # Login
        res = client.post("/api/auth/login", json={
            "username": "loginuser",
            "password": "password123",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "loginuser"

    def test_login_with_email(self, client):
        client.post("/api/auth/register", json={
            "username": "emaillogin",
            "email": "emaillogin@example.com",
            "password": "password123",
        })
        res = client.post("/api/auth/login", json={
            "username": "emaillogin@example.com",
            "password": "password123",
        })
        assert res.status_code == 200

    def test_login_invalid_credentials(self, client):
        client.post("/api/auth/register", json={
            "username": "realuser",
            "email": "real@example.com",
            "password": "password123",
        })
        res = client.post("/api/auth/login", json={
            "username": "realuser",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_login_missing_credentials(self, client):
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 400

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "username": "ghost",
            "password": "password123",
        })
        assert res.status_code == 401


class TestMe:
    def test_me_authenticated(self, client, auth_headers):
        res = client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["user"]["username"] == "testuser"

    def test_me_unauthenticated(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401


class TestRefresh:
    def test_refresh_token(self, client, refresh_headers):
        res = client.post("/api/auth/refresh", headers=refresh_headers)
        assert res.status_code == 200
        assert "access_token" in res.get_json()


class TestUpdateProfile:
    def test_update_display_name(self, client, auth_headers):
        res = client.patch("/api/auth/me", json={
            "display_name": "Updated Name",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["user"]["display_name"] == "Updated Name"

    def test_update_avatar_emoji(self, client, auth_headers):
        res = client.patch("/api/auth/me", json={
            "avatar_emoji": "🎉",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["user"]["avatar_emoji"] == "🎉"

    def test_update_profile_unauthenticated(self, client):
        res = client.patch("/api/auth/me", json={"display_name": "Hacker"})
        assert res.status_code == 401


class TestLogout:
    def test_logout(self, client):
        res = client.post("/api/auth/logout")
        assert res.status_code == 200
