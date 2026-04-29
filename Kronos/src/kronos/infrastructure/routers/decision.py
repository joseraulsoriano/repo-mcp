"""
Router de decisiones.

Endpoints para obtener decisiones del Policy Engine.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from kronos.application.services import DecisionService
from kronos.domain.entities import Decision as DomainDecision, Position
from kronos.infrastructure.dependencies import get_decision_service, create_decision_service_with_location

router = APIRouter()


class DecisionRequest(BaseModel):
    """Solicitud de decisión con ubicación opcional."""

    lat: Optional[float] = None
    lng: Optional[float] = None
    speed: Optional[float] = None  # m/s
    acceleration: Optional[float] = None  # m/s²
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    use_osm: Optional[bool] = False  # Usar OpenStreetMap para datos reales
    user_id: Optional[str] = None  # ID del usuario para usar su perfil


class DecisionResponse(BaseModel):
    """Respuesta de una decisión."""

    decision: str
    mode: str
    risk_score: float
    risk_level: str
    message: str
    confidence: float
    position: Optional[dict] = None

    @classmethod
    def from_domain(cls, decision: DomainDecision, position: Optional[Position] = None) -> "DecisionResponse":
        """Crea una respuesta desde una decisión del dominio."""
        response = cls(
            decision=decision.action.value,
            mode=decision.mode.value,
            risk_score=decision.risk_score.value,
            risk_level=decision.risk_score.level.value,
            message=decision.message,
            confidence=decision.confidence,
        )
        if position:
            response.position = {"lat": position.lat, "lng": position.lng}
        return response


@router.post("/decisions", response_model=DecisionResponse)
async def create_decision(request: Optional[DecisionRequest] = None):
    """
    Genera una decisión basada en el contexto actual o coordenadas específicas.

    Args:
        request: Solicitud opcional con coordenadas y parámetros

    Returns:
        Decisión del Policy Engine
    """
    try:
        if request and request.lat is not None and request.lng is not None:
            # Usar coordenadas específicas
            position = Position(lat=request.lat, lng=request.lng)
            destination = None
            if request.destination_lat and request.destination_lng:
                destination = Position(lat=request.destination_lat, lng=request.destination_lng)
            
            decision_service = create_decision_service_with_location(
                position=position,
                speed=request.speed,
                acceleration=request.acceleration,
                destination=destination,
                use_osm=request.use_osm if request.use_osm is not None else False,
                user_id=request.user_id,
            )
            decision = decision_service.decide()
            return DecisionResponse.from_domain(decision, position)
        else:
            # Usar configuración por defecto
            decision_service: DecisionService = get_decision_service()
            decision = decision_service.decide()
            return DecisionResponse.from_domain(decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar decisión: {str(e)}")


@router.get("/decisions", response_model=DecisionResponse)
async def get_decision(
    lat: Optional[float] = Query(None, description="Latitud"),
    lng: Optional[float] = Query(None, description="Longitud"),
    speed: Optional[float] = Query(None, description="Velocidad en m/s"),
    use_osm: Optional[bool] = Query(False, description="Usar OpenStreetMap para datos reales"),
    user_id: Optional[str] = Query(None, description="ID del usuario para usar su perfil"),
):
    """
    Obtiene una decisión basada en el contexto actual o coordenadas específicas.

    Args:
        lat: Latitud (opcional)
        lng: Longitud (opcional)
        speed: Velocidad en m/s (opcional)

    Returns:
        Decisión del Policy Engine
    """
    try:
        if lat is not None and lng is not None:
            # Usar coordenadas específicas
            position = Position(lat=lat, lng=lng)
            decision_service = create_decision_service_with_location(
                position=position,
                speed=speed,
                use_osm=use_osm if use_osm is not None else False,
                user_id=user_id,
            )
            decision = decision_service.decide()
            return DecisionResponse.from_domain(decision, position)
        else:
            # Usar configuración por defecto
            decision_service: DecisionService = get_decision_service()
            decision = decision_service.decide()
            return DecisionResponse.from_domain(decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar decisión: {str(e)}")
