"""
Infrastructure - Frameworks y servicios externos.

Capa externa que conecta el sistema con el mundo real:
FastAPI, proveedores de GPS, tráfico, mapas, etc.
"""

from kronos.infrastructure.api import create_app
from kronos.infrastructure.dependencies import create_decision_service_with_location
from kronos.infrastructure.providers import (
    GPSProvider,
    TrafficProvider,
    MapProvider,
)

__all__ = [
    "create_app",
    "create_decision_service_with_location",
    "GPSProvider",
    "TrafficProvider",
    "MapProvider",
]
