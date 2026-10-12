"""Local launcher that reads an optional backend .env file before app import."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "cybershield_api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=os.getenv("ENVIRONMENT", "development").casefold() not in {"production", "prod"},
    )
