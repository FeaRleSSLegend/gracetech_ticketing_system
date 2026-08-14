from fastapi.testclient import TestClient

from conftest import TestingSessionLocal
from core.security import hash_password
from main import app
from models.enums import NotificationKindEnum, RoleEnum, StatusEnum
from models.notification import Notification
from models.user import User

client = TestClient(app)


def make_employee(name="Emma Employee", email="emma@example.com", password="pw12345678"):
    """Signup always produces an employee, so the public route is enough."""
    body = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password},
    ).json()
    return body["token"], int(body["user"]["id"])


def make_admin(name="Adam Admin", email="adam@example.com", password="pw12345678"):
    """Admins cannot be self-registered, so insert one directly."""
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


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def open_ticket(token, comment="printer jammed", office="Finance", category="hardware"):
    return client.post(
        "/api/tickets/",
        json={"category": category, "comment": comment, "office": office},
        headers=bearer(token),
    ).json()


def notifications_for(name, token):
    return client.get(
        "/api/notifications/", params={"name": name}, headers=bearer(token)
    ).json()["notifications"]


def test_claim_then_resolve_succeeds():
    emp_token, _ = make_employee()
    admin_token, _ = make_admin()
    ticket = open_ticket(emp_token)

    claimed = client.post(
        f"/api/tickets/{ticket['id']}/claim", headers=bearer(admin_token)
    )
    assert claimed.status_code == 200
    assert claimed.json()["status"] == "in_progress"

    resolved = client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=bearer(admin_token),
    )

    assert resolved.status_code == 200
    body = resolved.json()
    assert body["status"] == "resolved"
    assert body["closedOn"] is not None
    assert body["assignedTo"] == "Adam Admin"


def test_resolve_notification_targets_the_creator():
    emp_token, emp_id = make_employee()
    admin_token, admin_id = make_admin()
    ticket = open_ticket(emp_token)

    client.post(f"/api/tickets/{ticket['id']}/claim", headers=bearer(admin_token))
    client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=bearer(admin_token),
    )

    db = TestingSessionLocal()
    try:
        note = (
            db.query(Notification)
            .filter(Notification.kind == NotificationKindEnum.resolved)
            .one()
        )
        # Targeted, not a broadcast: this is the difference from new_ticket/claimed.
        assert note.recipient_id == emp_id
        assert note.actor_id == admin_id
        assert note.ticket_id == ticket["id"]
        assert note.comment == "printer jammed"
    finally:
        db.close()


def test_employee_sees_their_targeted_notification_by_name():
    emp_token, _ = make_employee()
    admin_token, _ = make_admin()
    ticket = open_ticket(emp_token)

    client.post(f"/api/tickets/{ticket['id']}/claim", headers=bearer(admin_token))
    client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "closed"},
        headers=bearer(admin_token),
    )

    # The regression this covers: the lookup used to require role == admin, so
    # an employee's name matched nobody and returned only broadcasts.
    notes = notifications_for("Emma Employee", emp_token)
    kinds = {n["kind"] for n in notes}
    assert "closed" in kinds

    closed = next(n for n in notes if n["kind"] == "closed")
    assert closed["recipientName"] == "Emma Employee"
    assert closed["actorName"] == "Adam Admin"


def test_resolving_an_unclaimed_ticket_returns_409():
    emp_token, _ = make_employee()
    admin_token, _ = make_admin()
    ticket = open_ticket(emp_token)

    response = client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=bearer(admin_token),
    )

    assert response.status_code == 409
    assert "in progress" in response.json()["detail"]["error"]

    db = TestingSessionLocal()
    try:
        assert db.query(Notification).filter(
            Notification.kind.in_(
                [NotificationKindEnum.resolved, NotificationKindEnum.closed]
            )
        ).count() == 0
    finally:
        db.close()


def test_patch_rejects_open_and_in_progress():
    emp_token, _ = make_employee()
    admin_token, _ = make_admin()
    ticket = open_ticket(emp_token)
    client.post(f"/api/tickets/{ticket['id']}/claim", headers=bearer(admin_token))

    for bad in ("open", "in_progress"):
        response = client.patch(
            f"/api/tickets/{ticket['id']}",
            json={"status": bad},
            headers=bearer(admin_token),
        )
        assert response.status_code == 422, bad


def test_patch_is_admin_only_and_404s_for_missing_ticket():
    emp_token, _ = make_employee()
    admin_token, _ = make_admin()
    ticket = open_ticket(emp_token)
    client.post(f"/api/tickets/{ticket['id']}/claim", headers=bearer(admin_token))

    as_employee = client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=bearer(emp_token),
    )
    assert as_employee.status_code == 401

    missing = client.patch(
        "/api/tickets/9999", json={"status": "resolved"}, headers=bearer(admin_token)
    )
    assert missing.status_code == 404


def test_second_claim_conflicts_and_broadcast_still_visible():
    emp_token, _ = make_employee()
    first_token, _ = make_admin()
    second_token, _ = make_admin(name="Bea Admin", email="bea@example.com")
    ticket = open_ticket(emp_token)

    assert client.post(
        f"/api/tickets/{ticket['id']}/claim", headers=bearer(first_token)
    ).status_code == 200
    assert client.post(
        f"/api/tickets/{ticket['id']}/claim", headers=bearer(second_token)
    ).status_code == 409

    # claimed is a broadcast, so the admin who lost the race still sees it.
    notes = notifications_for("Bea Admin", second_token)
    claimed = [n for n in notes if n["kind"] == "claimed"]
    assert len(claimed) == 1
    assert claimed[0]["recipientName"] is None


def test_unknown_name_returns_empty_list():
    _, _ = make_employee()
    admin_token, _ = make_admin()

    assert notifications_for("Nobody At All", admin_token) == []


def test_status_enum_unchanged_for_tickets():
    """PATCH restricts inputs, but the ticket model still has all four states."""
    assert {s.value for s in StatusEnum} == {
        "open",
        "in_progress",
        "resolved",
        "closed",
    }
