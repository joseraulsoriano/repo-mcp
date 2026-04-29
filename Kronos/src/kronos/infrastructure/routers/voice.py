"""
Router de voz.

Endpoints para obtener audio de las decisiones del Policy Engine.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional

from kronos.application.services import DecisionService
from kronos.domain.entities import Position
from kronos.infrastructure.dependencies import get_decision_service, create_decision_service_with_location
from kronos.infrastructure.services.tts_service import TTSService, VoiceConfig
from kronos.infrastructure.services.tts_service_enhanced import (
    EnhancedTTSService,
    EnhancedVoiceConfig,
    get_best_tts_service,
)
from kronos.infrastructure.services.polly_tts_service import (
    get_polly_service_if_configured,
)

router = APIRouter()

# Instancia global del servicio TTS
_tts_service: Optional[TTSService] = None


def get_tts_service():
    """Obtiene el mejor servicio TTS disponible."""
    global _tts_service
    if _tts_service is None:
        try:
            # Usar servicio mejorado con slow=True para sonar más natural
            _tts_service = get_best_tts_service()
        except Exception:
            # Fallback a servicio básico con slow=True
            config = VoiceConfig(language="es", slow=True, tld="com.mx")
            _tts_service = TTSService(config=config)
    return _tts_service


@router.get("/audio")
async def get_decision_audio(
    lat: Optional[float] = Query(None, description="Latitud"),
    lng: Optional[float] = Query(None, description="Longitud"),
    speed: Optional[float] = Query(None, description="Velocidad en m/s"),
    use_osm: Optional[bool] = Query(False, description="Usar OpenStreetMap"),
    slow: Optional[bool] = Query(False, description="Hablar más lento"),
):
    """
    Obtiene audio de una decisión basada en coordenadas.

    Args:
        lat: Latitud (opcional)
        lng: Longitud (opcional)
        speed: Velocidad en m/s (opcional)
        use_osm: Usar OpenStreetMap para datos reales
        slow: Hablar más lento (útil en tráfico)

    Returns:
        Audio MP3 de la decisión
    """
    try:
        # Obtener decisión
        if lat is not None and lng is not None:
            position = Position(lat=lat, lng=lng)
            decision_service = create_decision_service_with_location(
                position=position,
                speed=speed,
                use_osm=use_osm if use_osm is not None else False,
            )
        else:
            decision_service: DecisionService = get_decision_service()

        decision = decision_service.decide()

        # Configurar TTS con velocidad si se especifica
        tts_service = get_tts_service()
        # Ya viene con slow=True por defecto para mejor calidad
        # Si se pide slow explícitamente, ya está configurado

        # Generar audio
        audio_data = tts_service.generate_decision_audio(
            message=decision.message,
            decision=decision.action.value,
        )

        # Retornar audio como respuesta
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="kronos_decision.mp3"',
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar audio: {str(e)}")


@router.post("/audio")
async def create_decision_audio_post(
    text: Optional[str] = Query(None, description="Texto a convertir a voz"),
    slow: Optional[bool] = Query(False, description="Hablar más lento"),
):
    """
    Convierte texto a voz (para pruebas).

    Args:
        text: Texto a convertir a voz
        slow: Hablar más lento

    Returns:
        Audio MP3 del texto
    """
    if not text:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro 'text'")

    try:
        tts_service = get_tts_service()
        # Ya viene con slow=True para mejor calidad
        audio_data = tts_service.text_to_speech(text)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="kronos_audio.mp3"',
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar audio: {str(e)}")


@router.get("/audio/text")
async def get_text_to_speech(
    text: str = Query(..., description="Texto a convertir a voz"),
    language: str = Query("es", description="Código de idioma (es, en, etc.)"),
    slow: bool = Query(False, description="Hablar más lento"),
):
    """
    Convierte texto arbitrario a voz.

    Args:
        text: Texto a convertir
        language: Código de idioma (default: es)
        slow: Hablar más lento

    Returns:
        Audio MP3 del texto
    """
    try:
        config = VoiceConfig(language=language, slow=slow, tld="com.mx")
        tts_service = TTSService(config=config)

        audio_data = tts_service.text_to_speech(text, language=language)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="kronos_tts.mp3"',
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar audio: {str(e)}")
