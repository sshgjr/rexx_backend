"""인증 관련 API 테스트"""


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "FastAPI server is running"


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_success(client):
    res = client.post("/register", json={
        "username": "홍길동",
        "email": "hong@example.com",
        "password": "securepass",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "hong@example.com"
    assert data["user"]["username"] == "홍길동"


def test_register_duplicate_email(client):
    payload = {
        "username": "유저1",
        "email": "dup@example.com",
        "password": "pass123",
    }
    client.post("/register", json=payload)
    res = client.post("/register", json=payload)
    assert res.status_code == 400
    assert "이미 존재하는 이메일" in res.json()["detail"]


def test_login_success(client):
    client.post("/register", json={
        "username": "로그인유저",
        "email": "login@example.com",
        "password": "mypassword",
    })
    res = client.post("/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "token" in data


def test_login_wrong_password(client):
    client.post("/register", json={
        "username": "유저",
        "email": "wrong@example.com",
        "password": "correctpass",
    })
    res = client.post("/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_login_nonexistent_email(client):
    res = client.post("/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })
    assert res.status_code == 401


def test_me_authenticated(client, auth_header):
    res = client.get("/me", headers=auth_header)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["email"] == "test@example.com"


def test_me_no_token(client):
    res = client.get("/me")
    assert res.status_code in (401, 403)
