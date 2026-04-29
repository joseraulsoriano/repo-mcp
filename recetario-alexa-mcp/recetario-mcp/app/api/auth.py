#!/usr/bin/env python3
"""
Validacion de API key para proteger el MCP.
Si API_KEY esta definida, las rutas /mcp/* y /tools requieren cabecera X-API-Key o Authorization: Bearer <key>.
/health queda abierto para probes.
"""
import os
from typing import Optional

from fastapi import Request, HTTPException


def get_api_key() -> str:
    return (os.getenv("API_KEY") or "").strip()


def is_protected() -> bool:
    return len(get_api_key()) > 0


def key_from_request(request: Request) -> str:
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization") or ""
    if isinstance(api_key, str) and api_key.lower().startswith("bearer "):
        return api_key[7:].strip()
    return (api_key or "").strip()


def require_api_key(request: Request) -> None:
    if not is_protected():
        return
    key = get_api_key()
    provided = key_from_request(request)
    if not provided or provided != key:
        raise HTTPException(status_code=401, detail="Unauthorized")
