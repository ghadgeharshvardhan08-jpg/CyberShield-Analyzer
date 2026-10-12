from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginInput, RegisterInput, SessionState, SuccessMessage, UserRead
from ..security import hash_password, rate_limit, verify_password
from ..dependencies import require_user

logger = logging.getLogger("cybershield")
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )


def _optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None
    return db.get(User, user_id)


@router.get("/session", response_model=SessionState)
def get_session(user: User | None = Depends(_optional_user)):
    return SessionState(authenticated=user is not None, user=_user_read(user) if user else None)


@router.post("/register", response_model=SessionState, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterInput, request: Request, db: Session = Depends(get_db)):
    rate_limit(request, "register", 5, 3600)
    user = User(
        email=str(payload.email).casefold(),
        display_name=payload.display_name,
        password_hash=hash_password(payload.password.get_secret_value()),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to create an account with those details.")
    request.session.clear()
    request.session["user_id"] = user.id
    logger.info("account created")
    return SessionState(authenticated=True, user=_user_read(user))


@router.post("/login", response_model=SessionState)
def login(payload: LoginInput, request: Request, db: Session = Depends(get_db)):
    rate_limit(request, "login", 10, 900)
    user = db.scalar(select(User).where(User.email == str(payload.email).casefold()))
    if user is None or not verify_password(payload.password.get_secret_value(), user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password was not recognized.")
    request.session.clear()
    request.session["user_id"] = user.id
    logger.info("account signed in")
    return SessionState(authenticated=True, user=_user_read(user))


@router.post("/logout", response_model=SuccessMessage)
def logout(request: Request):
    request.session.clear()
    return SuccessMessage(message="Signed out.")


@router.delete("/account", response_model=SuccessMessage)
def delete_account(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    db.delete(user)
    db.commit()
    request.session.clear()
    logger.info("account and owned records deleted")
    return SuccessMessage(message="Account and associated data deleted.")
