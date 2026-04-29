#!/usr/bin/env python3
"""
Proveedor de busqueda: Brave Search API (Web Search GET).
Documentacion: https://api-dashboard.search.brave.com/api-reference/web/search/get
Servicios: https://api-dashboard.search.brave.com/documentation/services/web-search

- Endpoint: GET https://api.search.brave.com/res/v1/web/search
- Auth: header X-Subscription-Token
- Params: q (required), count (max 20), country, search_lang, extra_snippets, freshness, offset
- Respuesta: web.results[] con title, url, description; opcional extra_snippets, age
"""
import os
import time
import calendar
from datetime import datetime, timezone
import urllib.parse
from typing import Any, Dict, List, Optional
import asyncio

import aiohttp

try:
    import redis  # type: ignore
except Exception:
    redis = None

BASE_URL = "https://api.search.brave.com/res/v1/web/search"
COUNT_MAX = 20  # API max per request (doc: count max 20)
OFFSET_MAX = 9  # API max offset (doc: offset max 9)


class ProviderSearch:
    def __init__(self):
        self.brave_api_key: Optional[str] = os.getenv("BRAVE_API_KEY")
        self.max_rps: float = float(os.getenv("BRAVE_MAX_RPS", "0.8"))
        self.monthly_quota: int = int(os.getenv("BRAVE_MONTHLY_QUOTA", "2000"))
        self._last_request_ts: float = 0.0
        self._rate_lock: Optional[asyncio.Lock] = None
        self._redis = None
        url = os.getenv("REDIS_URL") or ""
        if url and redis is not None:
            try:
                self._redis = redis.Redis.from_url(url, decode_responses=True)
            except Exception:
                self._redis = None

    def _build_params(
        self,
        query: str,
        topK: int = 10,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        extra_snippets: bool = False,
        freshness: Optional[str] = None,
        offset: int = 0,
    ) -> Dict[str, str]:
        """Parametros segun documentacion oficial Web Search GET."""
        count = min(max(1, topK), COUNT_MAX)
        params: Dict[str, str] = {
            "q": query,
            "count": str(count),
        }
        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if extra_snippets:
            params["extra_snippets"] = "true"
        if freshness:
            params["freshness"] = freshness  # pd, pw, pm, py
        if 0 <= offset <= OFFSET_MAX:
            params["offset"] = str(offset)
        return params

    async def _search_brave(
        self,
        query: str,
        topK: int = 10,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        extra_snippets: bool = False,
        freshness: Optional[str] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        if not self.brave_api_key:
            return {"results": [], "query": {"original": query, "more_results_available": False}}
        if not await self._respect_rps():
            return {"results": [], "query": {"original": query, "more_results_available": False}}
        if not await self._respect_monthly_quota():
            return {"results": [], "query": {"original": query, "more_results_available": False}}

        params = self._build_params(
            query, topK=topK, country=country, search_lang=search_lang,
            extra_snippets=extra_snippets, freshness=freshness, offset=offset,
        )
        url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.brave_api_key,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=12) as r:
                    if r.status != 200:
                        return {"results": [], "query": {"original": query, "more_results_available": False}}
                    data = await r.json()
            except Exception:
                return {"results": [], "query": {"original": query, "more_results_available": False}}

        raw_results = (data.get("web") or {}).get("results") or []
        query_info = data.get("query") or {}
        more = query_info.get("more_results_available", False)

        results: List[Dict[str, Any]] = []
        for item in raw_results[:topK]:
            r: Dict[str, Any] = {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
            }
            if item.get("age"):
                r["age"] = item.get("age")
            if item.get("extra_snippets"):
                r["extra_snippets"] = item.get("extra_snippets")
            results.append(r)

        return {"results": results, "query": {"original": query, "more_results_available": more}}

    async def _respect_rps(self) -> bool:
        if self.max_rps <= 0:
            return False
        min_interval = 1.0 / self.max_rps
        if self._rate_lock is None:
            self._rate_lock = asyncio.Lock()
        async with self._rate_lock:
            now = time.monotonic()
            wait_s = self._last_request_ts + min_interval - now
            if wait_s > 0:
                try:
                    await asyncio.sleep(wait_s)
                except Exception:
                    pass
            self._last_request_ts = time.monotonic()
        return True

    async def _respect_monthly_quota(self) -> bool:
        if self.monthly_quota <= 0:
            return False
        ym = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"brave:quota:{ym}"
        if self._redis is not None:
            try:
                val = self._redis.incr(key)
                now = datetime.now(timezone.utc)
                last_day = calendar.monthrange(now.year, now.month)[1]
                end_of_month = datetime(now.year, now.month, last_day, 23, 59, 59, tzinfo=timezone.utc)
                ttl = int((end_of_month - now).total_seconds())
                if ttl > 0:
                    self._redis.expire(key, ttl)
                if int(val) > self.monthly_quota:
                    return False
                return True
            except Exception:
                pass
        if not hasattr(self, "_monthly_counts"):
            setattr(self, "_monthly_counts", {})
        counts = getattr(self, "_monthly_counts")
        current = int(counts.get(ym, 0)) + 1
        counts[ym] = current
        if current > self.monthly_quota:
            return False
        return True

    async def search(
        self,
        query: str,
        topK: int = 10,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        extra_snippets: bool = False,
        freshness: Optional[str] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Web Search segun documentacion Brave.
        country: codigo 2 caracteres (ej. MX, US).
        search_lang: idioma contenido (ej. es, en).
        extra_snippets: hasta 5 fragmentos extra por resultado (doc).
        freshness: pd|pw|pm|py o rango custom.
        """
        return await self._search_brave(
            query,
            topK=topK,
            country=country,
            search_lang=search_lang,
            extra_snippets=extra_snippets,
            freshness=freshness,
            offset=offset,
        )


provider_search = ProviderSearch()
