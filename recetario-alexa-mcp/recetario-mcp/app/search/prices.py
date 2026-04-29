#!/usr/bin/env python3
"""
recetario.prices_search - Precios: Brave para encontrar paginas + scraping supermercados (Walmart, Soriana, Chedraui).
Sin APIs de tienda: scraping a paginas publicas.
"""
from typing import Any, Dict, List

from app.search.provider import provider_search
from app.scraping.supermarkets import scrape_prices_supermarkets

WALMART_DOMAIN = "walmart.com.mx"
SORIANA_DOMAIN = "soriana.com"
CHEDRAUI_DOMAIN = "chedraui.com.mx"


async def prices_search(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "").strip() or params.get("q", "").strip()
    product = params.get("product", "").strip() or query
    topK = min(int(params.get("topK", 5)), 15)
    use_scraping = params.get("scraping", True)

    if not product:
        product = "precio producto supermercado"

    res = await provider_search.search(
        f"{product} precio {WALMART_DOMAIN} OR {SORIANA_DOMAIN} OR {CHEDRAUI_DOMAIN}",
        topK=topK,
        country="MX",
        search_lang="es",
    )
    results = res.get("results") or []

    precios: List[Dict[str, Any]] = []
    seen_urls = set()

    for r in results:
        url = (r.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        precios.append({
            "title": r.get("title"),
            "url": url,
            "snippet": r.get("snippet"),
            "source": "brave",
            "price": None,
            "store": _infer_store(url),
        })

    if use_scraping and precios:
        scraped = await scrape_prices_supermarkets([p["url"] for p in precios[:5]])
        for i, p in enumerate(precios[: len(scraped)]):
            if i < len(scraped) and scraped[i]:
                p["price"] = scraped[i].get("price")
                p["store"] = scraped[i].get("store") or p.get("store")
                p["source"] = "scraping"

    return {"query": product, "precios": precios, "count": len(precios)}


def _infer_store(url: str) -> str:
    url_lower = url.lower()
    if WALMART_DOMAIN in url_lower:
        return "Walmart"
    if SORIANA_DOMAIN in url_lower:
        return "Soriana"
    if CHEDRAUI_DOMAIN in url_lower:
        return "Chedraui"
    return "Otro"
