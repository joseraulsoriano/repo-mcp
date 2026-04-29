#!/usr/bin/env python3
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.mcp.server import volunteer_mcp_server
from app.storage.education import get_edu_enriched, get_edu_details, get_edu_all_combined


def _career_soft_skills(career_name: str) -> set:
    """Mapea heurísticamente una carrera a soft skills relevantes."""
    n = (career_name or "").strip().lower()
    skills = set()
    if any(k in n for k in ["ingenier", "matem", "física", "fisica", "quim", "biolog", "sistemas", "comput"]):
        skills.update(["pensamiento analítico", "resolución de problemas", "trabajo en equipo", "aprendizaje continuo"])
    if any(k in n for k in ["arquitect", "diseñ", "diseno", "arte", "creativ"]):
        skills.update(["creatividad", "comunicación", "gestión del tiempo", "atención al detalle"])
    if any(k in n for k in ["psicolog", "educaci", "docencia", "pedagog"]):
        skills.update(["empatía", "comunicación", "escucha activa", "paciencia"])
    if any(k in n for k in ["derecho", "legal", "abog"]):
        skills.update(["comunicación", "negociación", "pensamiento crítico", "ética"])
    if any(k in n for k in ["medicina", "salud", "enfermer"]):
        skills.update(["empatía", "trabajo bajo presión", "trabajo en equipo", "ética"])
    if any(k in n for k in ["administraci", "gestión", "negocios", "empres"]):
        skills.update(["liderazgo", "planificación", "comunicación", "toma de decisiones"])
    if any(k in n for k in ["contadur", "finanz", "econom"]):
        skills.update(["atención al detalle", "pensamiento analítico", "ética", "gestión del tiempo"])
    if any(k in n for k in ["mercadotec", "marketing", "comercial", "publicidad"]):
        skills.update(["creatividad", "comunicación", "persuasión", "alfabetización de datos"])
    if any(k in n for k in ["relaciones internacionales", "relaciones", "internacional"]):
        skills.update(["negociación", "competencia intercultural", "comunicación", "resolución de conflictos"])
    if any(k in n for k in ["logística", "logistica", "cadenas", "operaciones"]):
        skills.update(["planificación", "organización", "comunicación", "resolución de problemas"])
    if not skills:
        skills.update(["comunicación", "trabajo en equipo", "pensamiento crítico"])
    return skills


def create_router(redis_client: Any = None, data_dir: str = "data") -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    @router.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @router.get("/tools")
    async def tools():
        return {"tools": volunteer_mcp_server.get_tools(), "count": len(volunteer_mcp_server.get_tools())}

    @router.post("/mcp/call")
    async def call(req: Dict[str, Any]):
        try:
            return await volunteer_mcp_server.handle_request(req)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/mcp/volunteer.prompt_search")
    async def prompt_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.prompt_search", "params": data})

    @router.post("/mcp/volunteer.search")
    async def search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.search", "params": data})

    @router.post("/mcp/volunteer.rank")
    async def rank(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.rank", "params": data})

    @router.post("/mcp/volunteer.subscribe_alerts")
    async def subscribe_alerts(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.subscribe_alerts", "params": data})

    @router.post("/mcp/volunteer.get_alerts")
    async def get_alerts(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.get_alerts", "params": data})

    @router.post("/mcp/volunteer.collect")
    async def collect(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.collect", "params": data})

    @router.post("/mcp/volunteer.mx_collect")
    async def mx_collect(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.mx_collect", "params": data})

    @router.post("/mcp/volunteer.mx_search")
    async def mx_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.mx_search", "params": data})

    @router.post("/mcp/volunteer.career_search")
    async def career_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.career_search", "params": data})

    @router.post("/mcp/education.search")
    async def education_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "education.search", "params": data})

    @router.post("/mcp/volunteer.area_search")
    async def area_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "volunteer.area_search", "params": data})

    @router.post("/mcp/jobs.search")
    async def jobs_search(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "jobs.search", "params": data})

    @router.post("/mcp/jobs.list")
    async def jobs_list(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "jobs.list", "params": data})

    @router.post("/mcp/learning.plan.save")
    async def learning_plan_save(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "learning.plan.save", "params": data})

    @router.post("/mcp/learning.plan.get")
    async def learning_plan_get(data: Dict[str, Any]):
        return await volunteer_mcp_server.handle_request({"tool": "learning.plan.get", "params": data})

    # Education GET endpoints (Redis o archivos)
    @router.get("/education/enriched")
    async def education_enriched():
        try:
            resp = get_edu_enriched(redis_client, data_dir)
            return resp
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/education/details")
    async def education_details():
        try:
            resp = get_edu_details(redis_client, data_dir)
            return resp
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/education/all")
    async def education_all():
        try:
            resp = get_edu_all_combined(redis_client, data_dir)
            return resp
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/education/skills")
    async def education_by_skills(
        skills: str = "",
        match: str = "all",
        state: str = "",
        tipo: str = "",
        limit: int = 50,
        offset: int = 0,
    ):
        try:
            resp = get_edu_all_combined(redis_client, data_dir)
            data = resp.get("data", [])
            requested = [s.strip().lower() for s in skills.split(",") if s.strip()] if skills else []
            match_all = (match or "all").lower() != "any"
            filtered = []
            for item in data:
                if state and (item.get("state") or "").lower() != state.strip().lower():
                    continue
                if tipo and (item.get("type") or "").lower() != tipo.strip().lower():
                    continue
                carreras = item.get("carreras") or []
                inferred = set()
                for c in carreras:
                    inferred.update(_career_soft_skills(str(c)))
                item_skills = sorted(inferred)
                enriched_item = dict(item)
                enriched_item["skills"] = item_skills
                if requested:
                    rs = set(requested)
                    present = set(s.lower() for s in item_skills)
                    ok = rs.issubset(present) if match_all else bool(rs & present)
                    if not ok:
                        continue
                filtered.append(enriched_item)
            total = len(filtered)
            return {
                "success": True,
                "total": total,
                "limit": limit,
                "offset": offset,
                "data": filtered[offset : offset + limit],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
