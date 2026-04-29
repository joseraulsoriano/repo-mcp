"""
Sistema de monitoreo y métricas.

Logging estructurado y métricas sin dependencias externas.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("kronos")


@dataclass
class Metric:
    """Métrica individual."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Colector de métricas simple.

    Almacena métricas en memoria (sin dependencias externas).
    Para producción, migrar a Prometheus o similar.
    """

    def __init__(self):
        """Inicializa el colector de métricas."""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)

    def increment(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Incrementa un contador."""
        self.counters[name] += 1
        logger.debug(f"Metric incremented: {name} (total: {self.counters[name]})", extra={"metric": name, "value": self.counters[name]})

    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Registra una métrica."""
        metric = Metric(name=name, value=value, tags=tags or {})
        self.metrics.append(metric)
        logger.debug(f"Metric recorded: {name}={value}", extra={"metric": name, "value": value})

    def timer(self, name: str):
        """
        Context manager para medir tiempo.

        Usage:
            with metrics.timer("decision_time"):
                decision = service.decide()
        """
        return TimerContext(self, name)

    def get_counter(self, name: str) -> int:
        """Obtiene valor de contador."""
        return self.counters.get(name, 0)

    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """Obtiene métricas filtradas por nombre."""
        if name:
            return [m for m in self.metrics if m.name == name]
        return self.metrics

    def get_stats(self) -> Dict:
        """Obtiene estadísticas agregadas."""
        stats = {
            "counters": dict(self.counters),
            "metrics_count": len(self.metrics),
            "timers": {},
        }

        # Calcular estadísticas de timers
        for timer_name, times in self.timers.items():
            if times:
                stats["timers"][timer_name] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }

        return stats


class TimerContext:
    """Context manager para medir tiempo."""

    def __init__(self, collector: MetricsCollector, name: str):
        """Inicializa el timer."""
        self.collector = collector
        self.name = name
        self.start_time = None

    def __enter__(self):
        """Inicia el timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finaliza el timer y registra la duración."""
        duration = time.time() - self.start_time
        self.collector.timers[self.name].append(duration)
        self.collector.record(f"{self.name}_duration", duration)
        logger.debug(f"Timer {self.name}: {duration:.3f}s")


# Instancia global del colector de métricas
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Obtiene la instancia global del colector de métricas."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Funciones helper para logging estructurado


def log_decision(decision_action: str, risk_score: float, confidence: float, **kwargs):
    """Log estructurado de decisión."""
    logger.info(
        "Decision made",
        extra={
            "action": decision_action,
            "risk_score": risk_score,
            "confidence": confidence,
            **kwargs,
        },
    )
    metrics = get_metrics_collector()
    metrics.increment(f"decisions.{decision_action}")
    metrics.record("decision.risk_score", risk_score)
    metrics.record("decision.confidence", confidence)


def log_error(error: Exception, context: Optional[Dict] = None):
    """Log estructurado de error."""
    logger.error(
        f"Error: {str(error)}",
        exc_info=True,
        extra={"error_type": type(error).__name__, "context": context or {}},
    )
    metrics = get_metrics_collector()
    metrics.increment("errors.total")
    metrics.increment(f"errors.{type(error).__name__}")


def log_osm_query(position: tuple, signal_count: int):
    """Log de consulta OSM."""
    logger.debug(
        f"OSM query: {position}, signals found: {signal_count}",
        extra={"position": position, "signal_count": signal_count},
    )
    metrics = get_metrics_collector()
    metrics.increment("osm.queries")
    metrics.record("osm.signals_found", signal_count)
