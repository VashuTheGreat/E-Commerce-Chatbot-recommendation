import json
import pytest

def test_api_health_check(api_client):
    """Test that the health check endpoint returns 200 and success."""
    response = api_client.get("/api/v1/common/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Server is fit and fine"


def test_api_available_time(api_client):
    """Test that the available_time endpoint returns the list of session durations."""
    response = api_client.get("/api/v1/common/available_time")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


def test_api_login_sets_cookie(api_client):
    """Test that login route sets cookie thread_id."""
    response = api_client.get("/api/v1/user/login/2")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "thread_id" in response.cookies
    assert response.cookies["thread_id"] == data["data"]


def test_api_chat_unauthorized(api_client):
    """Test that chat endpoint rejects requests without session cookie."""
    response = api_client.post(
        "/api/v1/agent/chat",
        data={"body": json.dumps({"thread_id": "test-thread", "message": "hello"})}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["success"] is False


def test_api_chat_authorized(api_client):
    """Test that chat endpoint accepts requests with cookie and streams mock response."""
    # First login to get a cookie
    login_res = api_client.get("/api/v1/user/login/2")
    thread_id = login_res.json()["data"]

    # Post chat request with cookie
    response = api_client.post(
        "/api/v1/agent/chat",
        data={"body": json.dumps({"thread_id": thread_id, "message": "Recommend some shoes"})},
        cookies={"thread_id": thread_id}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Read streamed chunks
    content = response.text
    assert "Mocked agent response" in content


def test_api_train_unauthorized(api_client):
    """Test that train endpoint rejects requests without session cookie."""
    response = api_client.get("/api/v1/model/train")
    assert response.status_code == 401
    assert response.json()["detail"]["success"] is False


def test_api_train_authorized(api_client):
    """Test that train endpoint initiates model training when authorized."""
    # First login to get a cookie
    login_res = api_client.get("/api/v1/user/login/2")
    thread_id = login_res.json()["data"]

    # Request train with cookie
    response = api_client.get(
        "/api/v1/model/train",
        cookies={"thread_id": thread_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "model Trained Succesfully"
    assert data["data"]["model_path"] == "dummy_model.pt"
