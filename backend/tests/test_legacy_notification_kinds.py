"""Regression cover for the production 500 on GET /api/notifications/.

Rows written before the assign -> claim rename still said kind='assigned',
which is no longer a member of NotificationKindEnum. SQLAlchemy raises
LookupError while hydrating such a row, so the whole endpoint 500s for any
name that matches a real user -- while an unmatched name returns 200, because
the early return means no rows are ever loaded.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from conftest import TestingSessionLocal
from core.security import hash_password
from main import app, migrate_legacy_notification_kinds
from models.enums import RoleEnum
from models.user import User

client = TestClient(app)
# Returns the 500 instead of re-raising, so we can assert on the status code.
crashing_client = TestClient(app, raise_server_exceptions=False)


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def legacy_row():
    """An admin, an employee's ticket, and one pre-rename notification row."""
    db = TestingSessionLocal()
    try:
        admin = User(name="gracetech", email="admin@gracetech.com",
                     password_hash=hash_password("gtadmin"), role=RoleEnum.admin)
        employee = User(name="Emma", email="emma@example.com",
                        password_hash=hash_password("pw12345678"),
                        role=RoleEnum.employee)
        db.add_all([admin, employee])
        db.commit()
        admin_id, employee_id = admin.id, employee.id

        db.execute(
            text("INSERT INTO tickets (id, category, comment, office, status,"
                 " created_by_id, is_new, created_at) VALUES"
                 " (1,'email','mail down','Finance','in_progress',:emp,0,"
                 " '2026-08-01 10:00:00')"),
            {"emp": employee_id},
        )
        db.execute(
            text("INSERT INTO notifications (kind, recipient_id, actor_id,"
                 " ticket_id, category, comment, created_at) VALUES"
                 " ('assigned', NULL, :admin, 1, 'email', 'mail down',"
                 " '2026-08-01 10:05:00')"),
            {"admin": admin_id},
        )
        db.commit()
    finally:
        db.close()

    token = client.post(
        "/api/auth/login",
        json={"email": "admin@gracetech.com", "password": "gtadmin"},
    ).json()["token"]
    return token


def kinds_in_db():
    db = TestingSessionLocal()
    try:
        return [r for r in db.execute(text("SELECT kind FROM notifications")).scalars()]
    finally:
        db.close()


def test_legacy_kind_crashes_the_endpoint_before_migration(legacy_row):
    """Documents the bug: this is the exact production failure."""
    response = crashing_client.get(
        "/api/notifications/", params={"name": "gracetech"}, headers=bearer(legacy_row)
    )
    assert response.status_code == 500


def test_unmatched_name_returns_200_even_with_legacy_rows(legacy_row):
    """Why it looked intermittent: no user match means no rows are loaded."""
    response = client.get(
        "/api/notifications/", params={"name": "Demo"}, headers=bearer(legacy_row)
    )
    assert response.status_code == 200
    assert response.json() == {"notifications": []}


def test_migration_fixes_the_endpoint(legacy_row):
    assert kinds_in_db() == ["assigned"]

    migrate_legacy_notification_kinds(TestingSessionLocal)

    assert kinds_in_db() == ["claimed"]

    response = client.get(
        "/api/notifications/", params={"name": "gracetech"}, headers=bearer(legacy_row)
    )
    assert response.status_code == 200
    notes = response.json()["notifications"]
    assert len(notes) == 1
    assert notes[0]["kind"] == "claimed"
    assert notes[0]["recipientName"] is None
    assert notes[0]["actorName"] == "gracetech"


def test_migration_is_idempotent_and_safe_on_a_clean_db(legacy_row):
    migrate_legacy_notification_kinds(TestingSessionLocal)
    migrate_legacy_notification_kinds(TestingSessionLocal)
    assert kinds_in_db() == ["claimed"]
