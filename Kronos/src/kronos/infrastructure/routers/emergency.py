"""
Router de emergencias (911).

Maneja situaciones de emergencia sin APIs externas.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from kronos.domain.entities import Position
from kronos.infrastructure.monitoring import get_metrics_collector, logger

router = APIRouter()


class EmergencyRequest(BaseModel):
    """Solicitud de emergencia."""

    lat: float
    lng: float
    emergency_type: str  # "accident", "medical", "breakdown", "other"
    description: Optional[str] = None
    user_id: Optional[str] = None


class EmergencyResponse(BaseModel):
    """Respuesta de emergencia."""

    emergency_id: str
    status: str  # "registered", "in_progress", "resolved"
    message: str
    location: dict
    timestamp: datetime
    next_steps: list


class EmergencyService:
    """
    Servicio de emergencias.

    Maneja registros de emergencias y proporciona información útil.
    No llama al 911 real, solo registra y proporciona ayuda.
    """

    def __init__(self):
        """Inicializa el servicio de emergencias."""
        self.emergencies: dict = {}
        self.metrics = get_metrics_collector()

    def register_emergency(
        self,
        position: Position,
        emergency_type: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> EmergencyResponse:
        """
        Registra una emergencia.

        Args:
            position: Posición de la emergencia
            emergency_type: Tipo de emergencia
            description: Descripción opcional
            user_id: ID del usuario (opcional)

        Returns:
            Respuesta de emergencia
        """
        import uuid

        emergency_id = str(uuid.uuid4())

        # Mensaje según tipo de emergencia
        messages = {
            "accident": "Accidente registrado. Si puedes, sal del tráfico. Usa las luces de emergencia. Ayuda en camino.",
            "medical": "Emergencia médica registrada. Busca un lugar seguro para detenerte. Ayuda médica en camino.",
            "breakdown": "Avería registrada. Si puedes, mueve la moto a un lugar seguro fuera del tráfico.",
            "other": "Emergencia registrada. Mantén la calma y busca un lugar seguro.",
        }

        message = messages.get(emergency_type, messages["other"])

        # Próximos pasos según tipo
        next_steps_map = {
            "accident": [
                "1. Sal del tráfico si puedes moverte",
                "2. Activa las luces de emergencia",
                "3. Llama al 911 desde tu teléfono",
                "4. No muevas a personas lesionadas",
                "5. Espera ayuda profesional",
            ],
            "medical": [
                "1. Detente en un lugar seguro",
                "2. Llama al 911 desde tu teléfono",
                "3. Describe tu ubicación exacta",
                "4. Sigue las instrucciones del operador",
                "5. Mantén tu teléfono accesible",
            ],
            "breakdown": [
                "1. Mueve la moto fuera del tráfico",
                "2. Activa las luces de emergencia",
                "3. Llama a asistencia vial",
                "4. Espera en un lugar seguro",
                "5. No intentes reparar en la carretera",
            ],
            "other": [
                "1. Busca un lugar seguro",
                "2. Llama al 911 desde tu teléfono",
                "3. Describe la situación",
                "4. Sigue las instrucciones",
            ],
        }

        next_steps = next_steps_map.get(emergency_type, next_steps_map["other"])

        # Crear respuesta
        response = EmergencyResponse(
            emergency_id=emergency_id,
            status="registered",
            message=message,
            location={"lat": position.lat, "lng": position.lng},
            timestamp=datetime.now(),
            next_steps=next_steps,
        )

        # Guardar emergencia
        self.emergencies[emergency_id] = {
            "id": emergency_id,
            "position": position,
            "type": emergency_type,
            "description": description,
            "user_id": user_id,
            "timestamp": datetime.now(),
            "status": "registered",
        }

        # Log y métricas
        logger.warning(
            "Emergency registered",
            extra={
                "emergency_id": emergency_id,
                "type": emergency_type,
                "location": {"lat": position.lat, "lng": position.lng},
                "user_id": user_id,
            },
        )
        self.metrics.increment("emergencies.registered")
        self.metrics.increment(f"emergencies.{emergency_type}")

        return response

    def get_emergency(self, emergency_id: str) -> Optional[dict]:
        """Obtiene información de una emergencia."""
        return self.emergencies.get(emergency_id)


# Instancia global del servicio
_emergency_service: Optional[EmergencyService] = None


def get_emergency_service() -> EmergencyService:
    """Obtiene la instancia global del servicio de emergencias."""
    global _emergency_service
    if _emergency_service is None:
        _emergency_service = EmergencyService()
    return _emergency_service


@router.post("/emergency", response_model=EmergencyResponse)
async def register_emergency(request: EmergencyRequest):
    """
    Registra una emergencia.

    **IMPORTANTE:** Este endpoint NO llama al 911 real.
    Solo registra la emergencia y proporciona información útil.
    El usuario DEBE llamar al 911 desde su teléfono.

    Args:
        request: Solicitud de emergencia

    Returns:
        Respuesta con información de emergencia y próximos pasos
    """
    try:
        position = Position(lat=request.lat, lng=request.lng)
        service = get_emergency_service()

        response = service.register_emergency(
            position=position,
            emergency_type=request.emergency_type,
            description=request.description,
            user_id=request.user_id,
        )

        return response
    except Exception as e:
        logger.error("Error registering emergency", exc_info=True, extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Error al registrar emergencia: {str(e)}")


@router.get("/emergency/{emergency_id}")
async def get_emergency(emergency_id: str):
    """Obtiene información de una emergencia registrada."""
    service = get_emergency_service()
    emergency = service.get_emergency(emergency_id)

    if not emergency:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    return emergency


@router.get("/emergency/status/health")
async def emergency_health_check():
    """
    Health check del servicio de emergencias.

    Retorna estadísticas del servicio.
    """
    service = get_emergency_service()
    stats = service.metrics.get_stats()

    return {
        "status": "operational",
        "emergencies_registered": len(service.emergencies),
        "metrics": stats,
    }
