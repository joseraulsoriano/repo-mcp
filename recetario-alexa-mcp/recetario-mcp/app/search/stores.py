#!/usr/bin/env python3
"""
recetario.stores_search - Supermercados / tiendas (Brave + dominios MX).
"""
from typing import Any, Dict, List

from app.search.provider import provider_search

STORE_DOMAINS = ["walmart.com.mx", "soriana.com", "chedraui.com.mx", "heb.com.mx", "lacomer.com.mx"]


async def stores_search(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "").strip() or params.get("q", "").strip()
    location = params.get("location", "").strip()
    topK = min(int(params.get("topK", 10)), 20)

    if not query:
        query = "supermercados Mexico"
    if location:
        query = f"{query} {location}"

    domain_part = " OR ".join(f"site:{d}" for d in STORE_DOMAINS[:5])
    boosted = f"{query} ({domain_part})"

    res = await provider_search.search(
        boosted,
        topK=topK,
        country="MX",
        search_lang="es",
    )
    results = res.get("results") or []

    stores: List[Dict[str, Any]] = []
    for r in results:
        url = (r.get("url") or "").strip()
        store_name = _infer_store_name(url)
        stores.append({
            "title": r.get("title"),
            "url": url,
            "snippet": r.get("snippet"),
            "store": store_name,
            "source": "brave",
        })

    return {"query": query, "stores": stores, "count": len(stores)}


def _infer_store_name(url: str) -> str:
    url_lower = url.lower()
    if "walmart" in url_lower:
        return "Walmart"
    if "soriana" in url_lower:
        return "Soriana"
    if "chedraui" in url_lower:
        return "Chedraui"
    if "heb" in url_lower:
        return "HEB"
    if "lacomer" in url_lower:
        return "La Comer"
    return "Otro"
