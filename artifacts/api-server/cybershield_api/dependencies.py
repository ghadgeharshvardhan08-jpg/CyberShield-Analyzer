from __future__ import annotations

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

session_cookie = APIKeyCookie(name="cybershield_session", auto_error=False)


def require_user(
    request: Request,
    _session_cookie: str | None = Security(session_cookie),
    db: Session = Depends(get_db),
) -> User:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    return user
