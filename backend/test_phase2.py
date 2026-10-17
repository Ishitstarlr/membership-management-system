import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.auth import hash_password

from sqlalchemy.pool import StaticPool

# Test database using StaticPool so all connections share the same in-memory DB
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_registration_success(client):
    res = client.post("/api/auth/register", json={"email": "member1@nitk.edu.in", "password": "password123"})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "member1@nitk.edu.in"
    # Mandatory requirement: Public registration must always assign MEMBER
    assert data["role"] == "MEMBER"
    assert "password_hash" not in data


def test_registration_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dupe@nitk.edu.in", "password": "password123"})
    res = client.post("/api/auth/register", json={"email": "dupe@nitk.edu.in", "password": "differentpass"})
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_registration_short_password(client):
    res = client.post("/api/auth/register", json={"email": "short@nitk.edu.in", "password": "123"})
    assert res.status_code == 422


def test_login_success_and_jwt(client):
    client.post("/api/auth/register", json={"email": "user@nitk.edu.in", "password": "mypassword"})
    res = client.post("/api/auth/login", json={"email": "user@nitk.edu.in", "password": "mypassword"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "MEMBER"
    assert data["email"] == "user@nitk.edu.in"


def test_login_invalid_credentials(client):
    client.post("/api/auth/register", json={"email": "valid@nitk.edu.in", "password": "mypassword"})
    # Wrong password
    res = client.post("/api/auth/login", json={"email": "valid@nitk.edu.in", "password": "wrongpassword"})
    assert res.status_code == 401
    # Nonexistent user
    res2 = client.post("/api/auth/login", json={"email": "ghost@nitk.edu.in", "password": "mypassword"})
    assert res2.status_code == 401


def test_get_me_protected(client):
    client.post("/api/auth/register", json={"email": "me@nitk.edu.in", "password": "password123"})
    login_res = client.post("/api/auth/login", json={"email": "me@nitk.edu.in", "password": "password123"})
    token = login_res.json()["access_token"]

    # Without token -> 401
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401

    # With valid token -> 200
    auth_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_res.status_code == 200
    assert auth_res.json()["email"] == "me@nitk.edu.in"


def test_rbac_admin_enforcement(client, test_db):
    # 1. Register a regular member
    client.post("/api/auth/register", json={"email": "regular@nitk.edu.in", "password": "password123"})
    member_login = client.post("/api/auth/login", json={"email": "regular@nitk.edu.in", "password": "password123"})
    member_token = member_login.json()["access_token"]

    # Member attempts admin-only action -> Must get 403 Forbidden
    member_admin_attempt = client.get("/api/auth/admin-check", headers={"Authorization": f"Bearer {member_token}"})
    assert member_admin_attempt.status_code == 403
    assert "Administrative privileges required" in member_admin_attempt.json()["detail"]

    # 2. Create an admin user directly in DB
    admin = User(email="admin@nitk.edu.in", password_hash=hash_password("adminpass"), role="ADMIN")
    test_db.add(admin)
    test_db.commit()

    admin_login = client.post("/api/auth/login", json={"email": "admin@nitk.edu.in", "password": "adminpass"})
    admin_token = admin_login.json()["access_token"]

    # Admin accesses admin-only action -> Must get 200 OK
    admin_attempt = client.get("/api/auth/admin-check", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_attempt.status_code == 200
    assert "Hello Admin" in admin_attempt.json()["message"]


def test_logout(client):
    client.post("/api/auth/register", json={"email": "logout@nitk.edu.in", "password": "password123"})
    login = client.post("/api/auth/login", json={"email": "logout@nitk.edu.in", "password": "password123"})
    token = login.json()["access_token"]

    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "Successfully logged out" in res.json()["message"]
