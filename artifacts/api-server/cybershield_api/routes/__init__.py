from fastapi import APIRouter

from .analyses import router as analyses_router
from .auth import router as auth_router
from .learning import router as learning_router
from .settings import router as settings_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(analyses_router)
router.include_router(learning_router)
router.include_router(settings_router)
