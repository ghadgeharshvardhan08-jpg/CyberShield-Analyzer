from __future__ import annotations

import logging
import os
from collections import deque
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .routes import router


class RequestBodyLimitMiddleware:
    """Bound buffered API request data even when Content-Length is absent."""

    def __init__(self, app, max_bytes: int = 16_384):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/api/"):
            await self.app(scope, receive, send)
            return

        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    if int(value) > self.max_bytes:
                        await JSONResponse(
                            {"detail": "Request body is too large."},
                            status_code=413,
                        )(scope, receive, send)
                        return
                except ValueError:
                    await JSONResponse({"detail": "Invalid request."}, status_code=400)(
                        scope, receive, send
                    )
                    return

        buffered = deque()
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                buffered.append(message)
                continue
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                await JSONResponse(
                    {"detail": "Request body is too large."},
                    status_code=413,
                )(scope, receive, send)
                return
            buffered.append(message)
            if not message.get("more_body", False):
                break

        async def replay_body():
            if buffered:
                return buffered.popleft()
            return await receive()

        await self.app(scope, replay_body, send)


def _origins() -> list[str]:
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]


def create_app() -> FastAPI:
    environment = os.getenv("ENVIRONMENT", "development").casefold()
    session_secret = os.getenv("SESSION_SECRET")
    if not session_secret and environment in {"production", "prod"}:
        raise RuntimeError("SESSION_SECRET must be configured in production.")
    if not session_secret:
        # Local-only default. Production deliberately fails closed above.
        session_secret = "cybershield-local-development-secret-change-me"

    app = FastAPI(
        title="CyberShield API",
        version="1.0.0",
        description=(
            "Educational, preliminary URL pattern analysis. Submitted addresses are never fetched."
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
        max_age=600,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        session_cookie="cybershield_session",
        max_age=12 * 60 * 60,
        same_site="lax",
        https_only=os.getenv("COOKIE_SECURE", "false").casefold() in {"1", "true", "yes"},
    )
    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=16_384)

    @app.get("/api/healthz", tags=["health"])
    def health_check():
        return {"status": "ok"}

    app.include_router(router)

    @app.middleware("http")
    async def security_and_request_guard(request: Request, call_next):
        if request.url.path.startswith("/api/"):
            if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
                origin = request.headers.get("origin")
                if origin:
                    allowed_origins = set(_origins())
                    request_host = request.headers.get("host", "").casefold()
                    origin_host = urlsplit(origin).netloc.casefold()
                    is_browser_same_origin = (
                        request.headers.get("sec-fetch-site", "").casefold() == "same-origin"
                    )
                    if (
                        origin.rstrip("/") not in allowed_origins
                        and origin_host != request_host
                        and not is_browser_same_origin
                    ):
                        return JSONResponse({"detail": "Request origin was not allowed."}, status_code=403)
                elif request.headers.get("sec-fetch-site", "").casefold() == "cross-site":
                    return JSONResponse({"detail": "Request origin was not allowed."}, status_code=403)

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def safe_validation_error(_request: Request, _exc: RequestValidationError):
        # Do not echo attacker-controlled inputs (which can contain credentials) into responses.
        return JSONResponse({"detail": "Request validation failed."}, status_code=422)

    @app.exception_handler(Exception)
    async def safe_unexpected_error(_request: Request, exc: Exception):
        # Avoid logging exception messages because a driver may include connection details.
        logging.getLogger("cybershield").error(
            "request failed unexpectedly (%s)",
            type(exc).__name__,
        )
        return JSONResponse({"detail": "The request could not be completed."}, status_code=500)

    return app


app = create_app()
