from fastapi.testclient import TestClient

from conftest import TestingSessionLocal
from core.security import hash_password
from main import app
from models.comment import Comment
from models.enums import RoleEnum, StatusEnum
from models.notification import Notification
from models.ticket import Ticket
from models.user import User

client = TestClient(app)


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def make_admin(name, email, password="pw12345678"):
    db = TestingSessionLocal()
    try:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=RoleEnum.admin,
        )
        db.add(user)
        db.commit()
        user_id = user.id
    finally:
        db.close()
    token = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    ).json()["token"]
    return token, user_id


def make_employee(name="Emma Employee", email="emma@example.com", password="pw12345678"):
    body = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password},
    ).json()
    return body["token"], int(body["user"]["id"])


def two_admins():
    keeper = make_admin("Keeper Admin", "keeper@example.com")
    doomed = make_admin("Doomed Admin", "doomed@example.com")
    return keeper, doomed


def test_delete_admin_succeeds():
    (keeper_token, _), (_, doomed_id) = two_admins()

    response = client.delete(f"/api/admins/{doomed_id}", headers=bearer(keeper_token))

    assert response.status_code == 200
    assert response.json()["admin"]["email"] == "doomed@example.com"

    listed = client.get("/api/admins/", headers=bearer(keeper_token)).json()
    assert [a["email"] for a in listed] == ["keeper@example.com"]


def test_delete_releases_claimed_tickets_and_clears_notifications():
    (keeper_token, _), (doomed_token, doomed_id) = two_admins()
    emp_token, _ = make_employee()

    ticket = client.post(
        "/api/tickets/",
        json={"category": "email", "comment": "mail down", "office": "Finance"},
        headers=bearer(emp_token),
    ).json()
    client.post(f"/api/tickets/{ticket['id']}/claim", headers=bearer(doomed_token))

    response = client.delete(f"/api/admins/{doomed_id}", headers=bearer(keeper_token))
    assert response.status_code == 200
    assert response.json()["ticketsReleased"] == 1

    db = TestingSessionLocal()
    try:
        released = db.get(Ticket, ticket["id"])
        # Back in the pool rather than stuck in_progress with nobody on it.
        assert released.assignee_id is None
        assert released.status == StatusEnum.open
        # The claim notification named a now-deleted actor, so it is gone.
        assert db.query(Notification).filter(
            Notification.actor_id == doomed_id
        ).count() == 0
        # The employee's own new_ticket broadcast survives.
        assert db.query(Notification).count() == 1
    finally:
        db.close()

    # And the released ticket can be claimed again.
    assert client.post(
        f"/api/tickets/{ticket['id']}/claim", headers=bearer(keeper_token)
    ).status_code == 200


def test_delete_keeps_comments_but_detaches_author():
    (keeper_token, _), (doomed_token, doomed_id) = two_admins()
    emp_token, _ = make_employee()
    ticket = client.post(
        "/api/tickets/",
        json={"category": "other", "comment": "x", "office": "Ops"},
        headers=bearer(emp_token),
    ).json()
    client.post(
        f"/api/comments/{ticket['id']}",
        json={"body": "looking into it"},
        headers=bearer(doomed_token),
    )

    assert client.delete(
        f"/api/admins/{doomed_id}", headers=bearer(keeper_token)
    ).status_code == 200

    db = TestingSessionLocal()
    try:
        comment = db.query(Comment).one()
        assert comment.body == "looking into it"
        assert comment.user_id is None
    finally:
        db.close()


def test_cannot_delete_yourself():
    (keeper_token, keeper_id), _ = two_admins()

    response = client.delete(f"/api/admins/{keeper_id}", headers=bearer(keeper_token))

    assert response.status_code == 400
    assert "your own" in response.json()["detail"]["error"]


def test_cannot_delete_the_last_admin():
    solo_token, solo_id = make_admin("Solo Admin", "solo@example.com")
    other_token, other_id = make_admin("Other Admin", "other@example.com")
    client.delete(f"/api/admins/{other_id}", headers=bearer(solo_token))

    # Only one admin left; deleting anyone now would lock everyone out.
    response = client.delete(f"/api/admins/{solo_id}", headers=bearer(solo_token))
    assert response.status_code in (400, 409)


def test_cannot_delete_admin_who_filed_tickets():
    (keeper_token, _), (doomed_token, doomed_id) = two_admins()
    client.post(
        "/api/tickets/",
        json={"category": "other", "comment": "my own ticket", "office": "IT"},
        headers=bearer(doomed_token),
    )

    response = client.delete(f"/api/admins/{doomed_id}", headers=bearer(keeper_token))

    assert response.status_code == 409
    assert "filed 1 ticket" in response.json()["detail"]["error"]


def test_delete_requires_admin_and_404s_sensibly():
    (keeper_token, _), (_, doomed_id) = two_admins()
    emp_token, emp_id = make_employee()

    assert client.delete(
        f"/api/admins/{doomed_id}", headers=bearer(emp_token)
    ).status_code == 401
    assert client.delete("/api/admins/9999", headers=bearer(keeper_token)).status_code == 404
    # An employee id is not an admin id.
    assert client.delete(
        f"/api/admins/{emp_id}", headers=bearer(keeper_token)
    ).status_code == 404
