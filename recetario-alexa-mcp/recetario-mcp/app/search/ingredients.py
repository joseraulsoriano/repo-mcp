#!/usr/bin/env python3
"""
recetario.ingredients_search - Busqueda de ingredientes (Brave + dominios).
"""
from typing import Any, Dict, List

from app.search.provider import provider_search


async def ingredients_search(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "").strip() or params.get("q", "").strip()
    topK = min(int(params.get("topK", 10)), 20)

    if not query:
        query = "ingredientes cocina mexicana"

    res = await provider_search.search(
        query,
        topK=topK,
        country="MX",
        search_lang="es",
        extra_snippets=True,
    )
    results = res.get("results") or []

    ingredientes: List[Dict[str, Any]] = []
    for r in results:
        ingredientes.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("snippet"),
            "extra_snippets": r.get("extra_snippets"),
            "source": "brave",
        })

    return {"query": query, "ingredientes": ingredientes, "count": len(ingredientes)}
