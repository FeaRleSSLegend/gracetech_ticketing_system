import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-0123456789abcdef-0123456789abcdef")
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
