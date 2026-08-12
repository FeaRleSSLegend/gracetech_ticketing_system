import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from dotenv import load_dotenv

# backend/.env for local development. On Render the environment is already
# populated from the dashboard and there is no .env file to find.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENV", "development").lower() == "production":
        raise RuntimeError(
            "SECRET_KEY is not set. Set it in the Render environment dashboard; "
            "without it every JWT would be signed with a publicly known key."
        )
    # Development only. Deliberately obvious, and never used when ENV=production.
    SECRET_KEY = "insecure-dev-key-not-for-production"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return (
        "pbkdf2_sha256$100000$"
        f"{base64.b64encode(salt).decode('utf-8')}"
        f"${base64.b64encode(derived_key).decode('utf-8')}"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("pbkdf2_sha256$"):
        return False

    _, iterations, salt_b64, derived_b64 = hashed_password.split("$", 3)
    salt = base64.b64decode(salt_b64.encode("utf-8"))
    expected = base64.b64decode(derived_b64.encode("utf-8"))
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        int(iterations),
    )
    return secrets.compare_digest(actual, expected)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
