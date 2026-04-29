#!/usr/bin/env python3
"""
recetario.recipes_search - Busqueda de recetas MX (Brave + dominios recetas).
"""
from typing import Any, Dict, List

from app.search.provider import provider_search

RECETA_DOMAINS = ["allrecipes.com", "recetasgratis.net", "cocinafacil.com.mx", "kiwilimon.com", "mexico.desertcart.com"]


async def recipes_search(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "").strip() or params.get("q", "").strip()
    tipo_comida = params.get("tipo_comida", "").strip().lower()
    topK = min(int(params.get("topK", 10)), 20)

    if not query:
        query = "recetas mexicanas"
    if tipo_comida and tipo_comida in ("desayuno", "comida", "cena"):
        query = f"{query} {tipo_comida}"

    domain_part = " OR ".join(f"site:{d}" for d in RECETA_DOMAINS[:3])
    boosted = f"{query} ({domain_part})"

    res = await provider_search.search(
        boosted,
        topK=topK,
        country="MX",
        search_lang="es",
        extra_snippets=True,
    )
    results = res.get("results") or []

    recetas: List[Dict[str, Any]] = []
    for r in results:
        recetas.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("snippet"),
            "extra_snippets": r.get("extra_snippets"),
            "source": "brave",
        })

    return {"query": query, "recetas": recetas, "count": len(recetas)}
