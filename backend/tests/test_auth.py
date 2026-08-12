import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from core.dependencies import get_current_user, get_db
from models.user import User


client = TestClient(app)


def clear_users():
    db = next(get_db())
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


def test_register_and_login_flow():
    clear_users()

    response = client.post(
        "/api/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )

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
    clear_users()

    client.post(
        "/api/auth/register",
        json={
            "name": "Alice",
            "email": "duplicate@example.com",
            "password": "secret123",
        },
    )

    duplicate_response = client.post(
        "/api/auth/register",
        json={
            "name": "Alice 2",
            "email": "duplicate@example.com",
            "password": "another-password",
        },
    )

    assert duplicate_response.status_code == 400


def test_wrong_password_returns_unauthorized():
    clear_users()

    client.post(
        "/api/auth/register",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "correct-password",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_token_can_be_used_for_protected_dependency():
    clear_users()

    client.post(
        "/api/auth/register",
        json={
            "name": "Carol",
            "email": "carol@example.com",
            "password": "secret789",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "secret789"},
    )

    token = login_response.json()["token"]
    db = next(get_db())
    try:
        user = get_current_user(token=token, db=db)
    finally:
        db.close()

    assert user.email == "carol@example.com"
