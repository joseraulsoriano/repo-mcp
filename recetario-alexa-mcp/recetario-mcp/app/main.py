#!/usr/bin/env python3
"""
Recetario MCP - Punto de entrada FastAPI.
Motor: Brave Search API + scraping supermercados (Walmart, Soriana, Chedraui).
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.api.routes import router
from app.api.auth import get_api_key, is_protected, key_from_request

app = FastAPI(title="Recetario MCP", version="1.0.0")


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Si API_KEY esta definida, exige X-API-Key o Authorization: Bearer en /mcp/* y /tools. /health libre."""

    async def dispatch(self, request: Request, call_next):
        path = (request.scope.get("path") or "").strip()
        if not is_protected():
            return await call_next(request)
        if path == "/health" or path == "/":
            return await call_next(request)
        if path.startswith("/mcp/") or path == "/tools":
            key = get_api_key()
            provided = key_from_request(request)
            if not provided or provided != key:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        return await call_next(request)


app.add_middleware(ApiKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8012, log_level="info", reload=True)
