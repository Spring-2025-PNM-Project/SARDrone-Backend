from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_tha_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_failure():
    response = client.post("/login", json={"username": "wrong2323443", "password": "wrongpass"})
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login_success():
    response = client.post("/login", json={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()

def test_status_requires_read_access():
    login_response = client.post("/login", json={"username": "testuser", "password": "password"})
    assert login_response.status_code == 200
    assert "token" in login_response.json()
    token = login_response.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/drone/1/info", headers=headers)
    assert response.status_code == 403


def test_status_requires_auth():
    response = client.get("/drone/1/info")
    assert response.status_code == 401

def test_drones_requires_auth():
    response = client.get("/login/drones")
    assert response.status_code == 401
    
'''def test_push_status_requires_auth():
    response = client.post("/drone/1/info", json = {
        "location": {"latitude": 37.3352, "longitude": -121.8811, "altitude": 5},
        "timestamp": 0,
        "status": "online"
    })
    assert response.status_code == 401'''