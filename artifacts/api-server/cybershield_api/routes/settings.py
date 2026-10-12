from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_user
from ..models import User
from ..schemas import Settings, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _settings(user: User) -> Settings:
    return Settings(email=user.email, display_name=user.display_name, created_at=user.created_at)


@router.get("", response_model=Settings)
def get_settings(user: User = Depends(require_user)):
    return _settings(user)


@router.patch("", response_model=Settings)
def update_settings(
    payload: SettingsUpdate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Provide a setting to update.")
    if "display_name" in changes and changes["display_name"] is not None:
        user.display_name = changes["display_name"]
    db.add(user)
    db.commit()
    db.refresh(user)
    return _settings(user)
