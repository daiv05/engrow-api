from unittest.mock import patch


def _register_and_login(client):
    client.post(
        "/auth/register",
        json={"email": "push@example.com", "password": "supersecret1", "display_name": "Push User"},
    )
    login = client.post("/auth/login", json={"email": "push@example.com", "password": "supersecret1"})
    return login.json()["access_token"]


def test_subscribe_then_test_push_sends_to_stored_subscription(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    sub_body = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/abc123",
        "keys": {"p256dh": "fake-p256dh", "auth": "fake-auth"},
    }
    response = client.post("/push/subscribe", json=sub_body, headers=headers)
    assert response.status_code == 204

    with patch("app.routers.push.webpush") as mock_webpush:
        response = client.post("/push/test", headers=headers)
    assert response.status_code == 204
    mock_webpush.assert_called_once()


def test_unsubscribe_removes_subscription(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    sub_body = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/xyz789",
        "keys": {"p256dh": "fake-p256dh", "auth": "fake-auth"},
    }
    client.post("/push/subscribe", json=sub_body, headers=headers)

    response = client.request(
        "DELETE", "/push/subscribe", json={"endpoint": sub_body["endpoint"]}, headers=headers
    )
    assert response.status_code == 204

    with patch("app.routers.push.webpush") as mock_webpush:
        client.post("/push/test", headers=headers)
    mock_webpush.assert_not_called()
