import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app


@pytest.fixture(scope="function")
def db_session():
    """각 테스트마다 독립된 인메모리 SQLite DB를 사용.
    StaticPool로 스레드 간 동일 커넥션 공유 (TestClient 스레드 호환).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """테스트용 FastAPI 클라이언트 (DB를 인메모리로 교체)."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """회원가입 완료된 사용자 정보 반환."""
    res = client.post("/register", json={
        "username": "테스트유저",
        "email": "test@example.com",
        "password": "password123",
    })
    return res.json()


@pytest.fixture
def auth_header(registered_user):
    """인증 헤더 반환."""
    return {"Authorization": f"Bearer {registered_user['token']}"}
