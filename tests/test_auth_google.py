from unittest.mock import patch


def test_google_login_creates_new_user(client):
    fake_payload = {"sub": "google-uid-123", "email": "new@example.com", "name": "New User"}
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", return_value=fake_payload):
        response = client.post("/auth/google", json={"id_token": "fake-token"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert "access_token" in body


def test_google_login_reuses_existing_user_by_sub(client):
    fake_payload = {"sub": "google-uid-456", "email": "repeat@example.com", "name": "Repeat User"}
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", return_value=fake_payload):
        first = client.post("/auth/google", json={"id_token": "fake-token"})
        second = client.post("/auth/google", json={"id_token": "fake-token"})
    assert first.json()["user"]["id"] == second.json()["user"]["id"]


def test_google_login_rejects_invalid_token(client):
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError("bad token")):
        response = client.post("/auth/google", json={"id_token": "invalid"})
    assert response.status_code == 401
