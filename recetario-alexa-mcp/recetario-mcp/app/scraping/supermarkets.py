#!/usr/bin/env python3
"""
Scraping de paginas de supermercados (Walmart, Soriana, Chedraui) para extraer precio y nombre.
Sin APIs de tienda: solo HTTP + parse HTML. Selectores pueden cambiar si las paginas actualizan.
"""
import re
from typing import Any, Dict, List, Optional
import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """Obtiene el HTML de una URL."""
    if not url or not url.startswith("http"):
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as r:
                if r.status != 200:
                    return None
                return await r.text()
    except Exception:
        return None


def _infer_store(url: str) -> str:
    url_lower = url.lower()
    if "walmart" in url_lower:
        return "Walmart"
    if "soriana" in url_lower:
        return "Soriana"
    if "chedraui" in url_lower:
        return "Chedraui"
    return "Otro"


def _parse_price_from_text(text: str) -> Optional[str]:
    """Extrae precio en formato MXN (ej. $12.50, 12.50, $ 99.00)."""
    if not text:
        return None
    text = text.replace(",", "")
    match = re.search(r"\$\s*(\d+\.?\d*)", text)
    if match:
        return match.group(1)
    match = re.search(r"(\d+\.?\d*)\s*(?:MXN|pesos)?", text, re.I)
    if match:
        return match.group(1)
    return None


def _parse_walmart(html: str, url: str) -> Dict[str, Any]:
    """Extrae precio y nombre de pagina Walmart (selectores pueden variar)."""
    out = {"url": url, "store": "Walmart", "price": None, "name": None}
    if not html:
        return out
    soup = BeautifulSoup(html, "lxml")
    price_sel = soup.select_one("[data-automation='product-price'], .price-main .price, [itemprop='price']")
    if price_sel:
        content = price_sel.get("content") or price_sel.get_text(strip=True)
        out["price"] = _parse_price_from_text(content)
    name_sel = soup.select_one("h1[data-automation='product-title'], .product-title, [itemprop='name']")
    if name_sel:
        out["name"] = name_sel.get_text(strip=True)[:200]
    return out


def _parse_soriana(html: str, url: str) -> Dict[str, Any]:
    """Extrae precio y nombre de pagina Soriana (selectores pueden variar)."""
    out = {"url": url, "store": "Soriana", "price": None, "name": None}
    if not html:
        return out
    soup = BeautifulSoup(html, "lxml")
    price_sel = soup.select_one(".price, [itemprop='price'], .product-price")
    if price_sel:
        content = price_sel.get("content") or price_sel.get_text(strip=True)
        out["price"] = _parse_price_from_text(content)
    name_sel = soup.select_one("h1, .product-name, [itemprop='name']")
    if name_sel:
        out["name"] = name_sel.get_text(strip=True)[:200]
    return out


def _parse_chedraui(html: str, url: str) -> Dict[str, Any]:
    """Extrae precio y nombre de pagina Chedraui (selectores pueden variar)."""
    out = {"url": url, "store": "Chedraui", "price": None, "name": None}
    if not html:
        return out
    soup = BeautifulSoup(html, "lxml")
    price_sel = soup.select_one(".price, [itemprop='price'], .product-price, [data-price]")
    if price_sel:
        content = price_sel.get("content") or price_sel.get("data-price") or price_sel.get_text(strip=True)
        out["price"] = _parse_price_from_text(str(content))
    name_sel = soup.select_one("h1, .product-name, [itemprop='name']")
    if name_sel:
        out["name"] = name_sel.get_text(strip=True)[:200]
    return out


def _parse_generic(html: str, url: str) -> Dict[str, Any]:
    """Fallback: intenta extraer cualquier precio/nombre en la pagina."""
    out = {"url": url, "store": _infer_store(url), "price": None, "name": None}
    if not html:
        return out
    soup = BeautifulSoup(html, "lxml")
    for sel in soup.select("[itemprop='price'], .price, [data-price]"):
        content = sel.get("content") or sel.get("data-price") or sel.get_text(strip=True)
        p = _parse_price_from_text(str(content))
        if p:
            out["price"] = p
            break
    for sel in soup.select("h1, [itemprop='name'], .product-title"):
        t = sel.get_text(strip=True)
        if t and len(t) < 300:
            out["name"] = t[:200]
            break
    return out


def _parse_by_store(html: str, url: str) -> Dict[str, Any]:
    url_lower = url.lower()
    if "walmart" in url_lower:
        return _parse_walmart(html, url)
    if "soriana" in url_lower:
        return _parse_soriana(html, url)
    if "chedraui" in url_lower:
        return _parse_chedraui(html, url)
    return _parse_generic(html, url)


async def scrape_prices_supermarkets(urls: List[str], timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Obtiene HTML de cada URL y extrae precio y nombre segun el dominio (Walmart, Soriana, Chedraui).
    Devuelve una lista con un dict por URL (price, name, store, url). Si falla, devuelve dict con price/name None.
    """
    if not urls:
        return []

    async def one(url: str) -> Dict[str, Any]:
        html = await fetch_html(url, timeout=timeout)
        return _parse_by_store(html or "", url)

    results = await asyncio.gather(*[one(u) for u in urls[:10]], return_exceptions=True)
    out: List[Dict[str, Any]] = []
    for r in results:
        if isinstance(r, Exception):
            out.append({"url": "", "store": "Otro", "price": None, "name": None})
        else:
            out.append(r)
    return out
