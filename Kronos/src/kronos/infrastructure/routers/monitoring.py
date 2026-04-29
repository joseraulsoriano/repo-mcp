"""
Router de monitoreo y métricas.

Endpoints para consultar métricas y estadísticas.
"""

from fastapi import APIRouter

from kronos.infrastructure.monitoring import get_metrics_collector

router = APIRouter()


@router.get("/metrics/stats")
async def get_metrics_stats():
    """
    Obtiene estadísticas de métricas.

    Returns:
        Estadísticas agregadas de métricas
    """
    metrics = get_metrics_collector()
    return metrics.get_stats()


@router.get("/metrics/health")
async def get_metrics_health():
    """
    Health check con métricas básicas.

    Returns:
        Estado de salud con métricas
    """
    metrics = get_metrics_collector()
    stats = metrics.get_stats()

    return {
        "status": "healthy",
        "metrics": {
            "decisions_total": stats["counters"].get("decisions.total", 0),
            "errors_total": stats["counters"].get("errors.total", 0),
            "emergencies_total": stats["counters"].get("emergencies.registered", 0),
        },
        "timers": stats["timers"],
    }
