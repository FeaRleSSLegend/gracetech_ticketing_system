import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.security import hash_password
from database import SessionLocal, init_db
from models.enums import RoleEnum
from models.user import User
from routers import admins, auth, comments, notifications, tickets

# uvicorn configures this logger at INFO level, so these lines land in Render's
# logs alongside the server's own startup output.
logger = logging.getLogger("uvicorn.error")


def seed_admin_from_env() -> None:
    """Create the first admin from ADMIN_* env vars, if all three are set.

    Runs once per startup. Never raises: a failure here is logged and the app
    starts anyway. Local development with no ADMIN_* vars set is unaffected and
    logs nothing.
    """
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    name = os.getenv("ADMIN_NAME")

    if not email or not password or not name:
        return

    db = None
    try:
        db = SessionLocal()
        existing = db.query(User).filter(User.email == email).first()
        if existing is not None:
            logger.info("Admin already exists, skipping seed")
            return

        db.add(
            User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                role=RoleEnum.admin,
            )
        )
        db.commit()
        logger.info("Seeded admin account: %s", email)
    except Exception:
        if db is not None:
            db.rollback()
        # exception() logs the traceback without re-raising, so startup continues.
        logger.exception("Admin seeding failed, continuing startup")
    finally:
        if db is not None:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Enterprise IT Support Ticketing System", lifespan=lifespan)

init_db()
seed_admin_from_env()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "https://grace-tech-ticketing-system-fronten.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(admins.router, prefix="/api/admins", tags=["admins"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(
    notifications.router, prefix="/api/notifications", tags=["notifications"]
)
