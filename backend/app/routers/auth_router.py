"""Login / current-user endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str
    username: str
    full_name: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=payload.username.strip()).first()
    if not user or not auth.verify_password(payload.password, user.password_hash, user.salt):
        raise HTTPException(401, "Invalid username or password")
    return TokenOut(token=auth.create_token(user.username),
                    username=user.username, full_name=user.full_name)


@router.get("/me", response_model=TokenOut)
def me(user: models.User = Depends(auth.require_auth)):
    return TokenOut(token="", username=user.username, full_name=user.full_name)


@router.post("/change-password")
def change_password(payload: PasswordChange, db: Session = Depends(get_db),
                    user: models.User = Depends(auth.require_auth)):
    if not auth.verify_password(payload.current_password, user.password_hash, user.salt):
        raise HTTPException(400, "Current password is incorrect")
    if len(payload.new_password) < 4:
        raise HTTPException(400, "New password too short")
    user.password_hash, user.salt = auth.hash_password(payload.new_password)
    db.commit()
    return {"status": "ok"}
