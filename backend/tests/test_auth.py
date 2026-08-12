import os
import sys
import tempfile
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import models  # noqa: F401  (registers every model on Base.metadata)
from core.dependencies import get_db
from core.security import create_access_token
from database import Base
from main import app
from models.enums import RoleEnum
from models.user import User

# The tests run against their own throwaway database, never the dev
# ticketdatabase.db, so they neither depend on nor destroy real data.
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "gracetech_test_auth.db")
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


def register(**overrides):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
    }
    payload.update(overrides)
    return client.post("/api/auth/register", json=payload)


def test_register_and_login_flow():
    response = register()

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["email"] == "alice@example.com"
    assert payload["user"]["name"] == "Alice"
    # Register issues a token too, so the client is logged in straight after signup.
    assert payload["token"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )

    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert "token" in login_payload
    assert login_payload["user"]["email"] == "alice@example.com"


def test_duplicate_email_returns_bad_request():
    register(email="duplicate@example.com")
    duplicate_response = register(name="Alice 2", email="duplicate@example.com")

    assert duplicate_response.status_code == 400


def test_wrong_password_returns_unauthorized():
    register(email="bob@example.com", password="correct-password")

    response = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_token_can_be_used_for_protected_dependency():
    register(email="carol@example.com", password="secret789")
    login_response = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "secret789"},
    )
    token = login_response.json()["token"]

    response = client.get(
        "/api/tickets/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_register_always_creates_employee_even_if_role_sent():
    """A client must not be able to make itself an admin at signup."""
    response = register(email="sneaky@example.com", role="admin")

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "employee"

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "sneaky@example.com").first()
        assert user.role == RoleEnum.employee
    finally:
        db.close()


def test_self_registered_user_cannot_reach_admin_only_route():
    token = register(email="nobody@example.com", role="admin").json()["token"]

    response = client.post(
        "/api/admins/",
        json={"name": "Mallory", "email": "mallory@example.com", "password": "pw123456"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_expired_token_returns_401_not_500():
    register(email="expired@example.com")

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "expired@example.com").first()
        user_id = user.id
    finally:
        db.close()

    expired_token = create_access_token(
        {"sub": str(user_id)}, expires_delta=timedelta(minutes=-5)
    )

    response = client.get(
        "/api/tickets/", headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
