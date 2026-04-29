#!/usr/bin/env python3
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.mcp.server import recetario_mcp_server

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "recetario-mcp", "timestamp": datetime.now().isoformat()}


@router.get("/tools")
async def tools():
    return {"tools": recetario_mcp_server.get_tools(), "count": len(recetario_mcp_server.get_tools())}


@router.post("/mcp/call")
async def call(req: Dict[str, Any]):
    try:
        return await recetario_mcp_server.handle_request(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/recetario.recipes_search")
async def recipes_search(data: Dict[str, Any]):
    return await recetario_mcp_server.handle_request({"tool": "recetario.recipes_search", "params": data})


@router.post("/mcp/recetario.ingredients_search")
async def ingredients_search(data: Dict[str, Any]):
    return await recetario_mcp_server.handle_request({"tool": "recetario.ingredients_search", "params": data})


@router.post("/mcp/recetario.prices_search")
async def prices_search(data: Dict[str, Any]):
    return await recetario_mcp_server.handle_request({"tool": "recetario.prices_search", "params": data})


@router.post("/mcp/recetario.stores_search")
async def stores_search(data: Dict[str, Any]):
    return await recetario_mcp_server.handle_request({"tool": "recetario.stores_search", "params": data})
