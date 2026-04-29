#!/usr/bin/env python3
"""
Volunteer MCP - Punto de entrada FastAPI.
Arquitectura: app/ (api, mcp, search, storage, ranking).
"""
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    import redis  # type: ignore
except Exception:
    redis = None

load_dotenv()

from app.api.routes import create_router

app = FastAPI(title="Volunteer MCP", version="1.0.0")

_redis: Any = None
_redis_url = os.getenv("REDIS_URL") or ""
if _redis_url and redis is not None:
    try:
        _redis = redis.Redis.from_url(_redis_url, decode_responses=True)
    except Exception:
        _redis = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_data_dir = os.getenv("DATA_DIR", "data")
router = create_router(redis_client=_redis, data_dir=_data_dir)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8011, log_level="info", reload=True)
