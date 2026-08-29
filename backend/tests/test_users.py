from fastapi.testclient import TestClient

from conftest import TestingSessionLocal
from core.security import hash_password
from main import app
from models.comment import Comment
from models.enums import RoleEnum
from models.notification import Notification
from models.user import User

client = TestClient(app)


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def make_employee(name="Emma Employee", email="emma@example.com", password="pw12345678"):
    body = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password},
    ).json()
    return body["token"], int(body["user"]["id"])


def make_admin(name="Adam Admin", email="adam@example.com", password="pw12345678"):
    db = TestingSessionLocal()
    try:
        user = User(name=name, email=email,
                    password_hash=hash_password(password), role=RoleEnum.admin)
        db.add(user)
        db.commit()
        user_id = user.id
    finally:
        db.close()
    token = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    ).json()["token"]
    return token, user_id


def test_get_users_returns_only_employees():
    admin_token, admin_id = make_admin()
    _, emma_id = make_employee()
    make_employee(name="Eli Employee", email="eli@example.com")

    response = client.get("/api/users/", headers=bearer(admin_token))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"users"}
    emails = [u["email"] for u in body["users"]]
    assert emails == ["emma@example.com", "eli@example.com"]
    # The admin is absent from this list.
    assert "adam@example.com" not in emails
    # Minimal shape only: no password_hash, no role, no created_at.
    assert set(body["users"][0]) == {"id", "name", "email"}
    assert isinstance(body["users"][0]["id"], int)


def test_get_users_is_admin_only():
    make_admin()
    emp_token, _ = make_employee()

    denied = client.get("/api/users/", headers=bearer(emp_token))
    assert denied.status_code == 401  # require_role uses 401 throughout this codebase

    # No token at all: HTTPBearer rejects before require_role is reached.
    assert client.get("/api/users/").status_code == 401


def test_delete_employee_succeeds():
    admin_token, _ = make_admin()
    _, emma_id = make_employee()

    response = client.delete(f"/api/users/{emma_id}", headers=bearer(admin_token))

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/users/", headers=bearer(admin_token)).json()["users"] == []


def test_delete_refuses_admin_accounts():
    admin_token, _ = make_admin()
    _, other_admin_id = make_admin(name="Bea Admin", email="bea@example.com")

    response = client.delete(f"/api/users/{other_admin_id}", headers=bearer(admin_token))

    assert response.status_code == 403
    assert "admins endpoint" in response.json()["detail"]["error"]

    # Still there.
    admins = client.get("/api/admins/", headers=bearer(admin_token)).json()
    assert "bea@example.com" in [a["email"] for a in admins]


def test_delete_missing_user_404s():
    admin_token, _ = make_admin()
    assert client.delete("/api/users/9999", headers=bearer(admin_token)).status_code == 404


def test_delete_is_admin_only():
    make_admin()
    emp_token, emp_id = make_employee()
    other_token, other_id = make_employee(name="Eli", email="eli@example.com")

    assert client.delete(
        f"/api/users/{other_id}", headers=bearer(emp_token)
    ).status_code == 401


def test_delete_blocked_for_employee_with_tickets():
    admin_token, _ = make_admin()
    emp_token, emp_id = make_employee()
    client.post(
        "/api/tickets/",
        json={"category": "email", "comment": "mail down", "office": "Finance"},
        headers=bearer(emp_token),
    )

    response = client.delete(f"/api/users/{emp_id}", headers=bearer(admin_token))

    assert response.status_code == 409
    assert "existing tickets" in response.json()["detail"]["error"]
    # Not partially deleted.
    assert len(client.get("/api/users/", headers=bearer(admin_token)).json()["users"]) == 1


def test_delete_ticketless_employee_clears_their_comments_and_notifications():
    admin_token, admin_id = make_admin()
    author_token, author_id = make_employee(name="Author", email="author@example.com")
    helper_token, helper_id = make_employee(name="Helper", email="helper@example.com")

    # The ticket belongs to Author, so Helper stays ticket-free and deletable.
    ticket = client.post(
        "/api/tickets/",
        json={"category": "other", "comment": "x", "office": "Ops"},
        headers=bearer(author_token),
    ).json()
    client.post(
        f"/api/comments/{ticket['id']}",
        json={"body": "I saw this too"},
        headers=bearer(helper_token),
    )

    assert client.delete(
        f"/api/users/{helper_id}", headers=bearer(admin_token)
    ).status_code == 204

    db = TestingSessionLocal()
    try:
        comment = db.query(Comment).one()
        assert comment.body == "I saw this too"
        assert comment.user_id is None
        assert db.query(Notification).filter(
            Notification.actor_id == helper_id
        ).count() == 0
        # Author's own new_ticket notification is untouched.
        assert db.query(Notification).count() == 1
    finally:
        db.close()
