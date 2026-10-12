from __future__ import annotations

import hashlib
import threading
import time
from collections import defaultdict, deque

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError
from fastapi import HTTPException, Request


password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = threading.Lock()
_last_sweep = 0.0


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        return password_hasher.verify(encoded_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def rate_limit(request: Request, bucket: str, limit: int, window_seconds: int, subject: str | None = None) -> None:
    """Small per-process sliding-window limiter; keys never retain clear IP addresses."""
    global _last_sweep
    address = request.client.host if request.client else "unknown"
    digest = hashlib.sha256(address.encode("utf-8")).hexdigest()[:24]
    key = f"{bucket}:{subject or digest}"
    now = time.monotonic()
    with _lock:
        if now - _last_sweep >= 300:
            stale = [stored_key for stored_key, times in _attempts.items() if not times or now - times[-1] >= 3600]
            for stored_key in stale:
                _attempts.pop(stored_key, None)
            _last_sweep = now
        attempts = _attempts[key]
        while attempts and now - attempts[0] >= window_seconds:
            attempts.popleft()
        if len(attempts) >= limit:
            retry_after = max(1, int(window_seconds - (now - attempts[0])))
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait before trying again.",
                headers={"Retry-After": str(retry_after)},
            )
        attempts.append(now)
