"""Authentication: password hashing (PBKDF2) and HMAC-signed bearer tokens.

Uses only the Python standard library — no extra dependencies. Tokens are
stateless: `base64(username.expiry).hmac_sig`. The signing secret comes from the
SECRET_KEY env var (set one in production); otherwise a per-boot random key is
used (users simply re-login after a restart).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .database import get_db
from . import models

SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days
_PBKDF2_ROUNDS = 100_000


# --- Password hashing -------------------------------------------------------
def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return dk.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    calc, _ = hash_password(password, salt)
    return hmac.compare_digest(calc, password_hash)


# --- Tokens -----------------------------------------------------------------
def _sign(payload: str) -> str:
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return sig


def create_token(username: str) -> str:
    payload = f"{username}.{int(time.time()) + TOKEN_TTL_SECONDS}"
    b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    return f"{b64}.{_sign(payload)}"


def verify_token(token: str) -> str | None:
    """Return the username if the token is valid and unexpired, else None."""
    try:
        b64, sig = token.rsplit(".", 1)
        payload = base64.urlsafe_b64decode(b64.encode()).decode()
        if not hmac.compare_digest(_sign(payload), sig):
            return None
        username, exp = payload.rsplit(".", 1)
        if int(exp) < int(time.time()):
            return None
        return username
    except Exception:
        return None


# --- FastAPI dependency -----------------------------------------------------
def require_auth(authorization: str | None = Header(default=None),
                 db: Session = Depends(get_db)) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Not authenticated")
    token = authorization.split(" ", 1)[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(models.User).filter_by(username=username).first()
    if not user:
        raise HTTPException(401, "User no longer exists")
    return user
