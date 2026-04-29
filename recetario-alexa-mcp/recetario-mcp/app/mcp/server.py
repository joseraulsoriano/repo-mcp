#!/usr/bin/env python3
"""
Recetario MCP - Servidor MCP para recetas, ingredientes, precios y supermercados (MX).
Tools: Brave Search API + scraping supermercados (Walmart, Soriana, Chedraui).
"""
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from app.search.recipes import recipes_search
from app.search.ingredients import ingredients_search
from app.search.prices import prices_search
from app.search.stores import stores_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecetarioMCPServer:
    def __init__(self):
        self.tools = {
            "recetario.recipes_search": self._recipes_search,
            "recetario.ingredients_search": self._ingredients_search,
            "recetario.prices_search": self._prices_search,
            "recetario.stores_search": self._stores_search,
        }
        self.stats = {
            "requests": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
            "tool_metrics": {},
        }

    def get_tools(self) -> List[str]:
        return list(self.tools.keys())

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.stats["requests"] += 1
            tool = request.get("tool", "")
            params = request.get("params", {})

            if tool not in self.tools:
                return {"success": False, "error": f"Tool not found: {tool}", "available_tools": self.get_tools()}

            start = time.perf_counter()
            result = await self.tools[tool](params)
            duration_ms = (time.perf_counter() - start) * 1000.0

            tm = self.stats["tool_metrics"].setdefault(tool, {"calls": 0, "total_ms": 0.0, "avg_ms": 0.0, "last_ms": 0.0})
            tm["calls"] += 1
            tm["total_ms"] += duration_ms
            tm["last_ms"] = duration_ms
            tm["avg_ms"] = tm["total_ms"] / max(1, tm["calls"])

            return {
                "success": True,
                "result": result,
                "tool": tool,
                "duration_ms": round(duration_ms, 2),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Error: %s", e)
            return {"success": False, "error": str(e)}

    async def _recipes_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await recipes_search(params)

    async def _ingredients_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await ingredients_search(params)

    async def _prices_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await prices_search(params)

    async def _stores_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await stores_search(params)


recetario_mcp_server = RecetarioMCPServer()
