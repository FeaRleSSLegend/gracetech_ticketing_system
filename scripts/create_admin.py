"""One-time seed script: create the first admin account.

Run it directly, from anywhere:

    python scripts/create_admin.py

It goes through SessionLocal, so it targets whatever DATABASE_URL points at --
the local SQLite file by default, or Postgres on Render. There is deliberately
no HTTP route that does this; every admin after the first is created through
POST /admins by an existing admin.
"""

import getpass
import os
import sys

# The backend package lives one level down from the repo root; make its modules
# importable no matter which directory this is run from.
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from core.security import hash_password  # noqa: E402
from database import SessionLocal  # noqa: E402
from models.enums import RoleEnum  # noqa: E402
from models.user import User  # noqa: E402


def main() -> int:
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    if not name or not email or not password:
        print("Name, email and password are all required. Nothing was created.")
        return 1

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing is not None:
            print(
                f"A user with email {email!r} already exists "
                f"(id={existing.id}, role={existing.role.value}). Nothing was created."
            )
            return 1

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=RoleEnum.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Created admin id={admin.id} email={admin.email}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
