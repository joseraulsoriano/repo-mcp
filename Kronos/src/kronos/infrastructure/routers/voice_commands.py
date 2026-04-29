"""
Router para comandos de voz.

Procesa comandos de voz como "Kronos vamos a tal lugar".
"""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from kronos.domain.entities import Position
from kronos.infrastructure.services.stt_service import STTService

router = APIRouter()

# Instancia global del servicio STT
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Obtiene el servicio STT."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service


class VoiceCommandRequest(BaseModel):
    """Solicitud de comando de voz."""

    text: str  # Texto del comando después de STT
    user_id: Optional[str] = None  # ID del usuario (opcional)


class VoiceCommandResponse(BaseModel):
    """Respuesta de comando de voz procesado."""

    action: str  # Acción (ej: "navigate")
    destination: Optional[str] = None  # Destino normalizado
    destination_coords: Optional[dict] = None  # Coordenadas del destino (si se encuentra)
    message: str  # Mensaje de respuesta
    success: bool  # Si el comando fue procesado correctamente


@router.post("/voice/command/text")
async def process_voice_command_text(request: VoiceCommandRequest):
    """
    Procesa un comando de voz en formato texto.

    Ejemplo: "Kronos vamos a trabajo"

    Args:
        request: Comando de voz en texto

    Returns:
        Respuesta con destino y acción
    """
    try:
        stt_service = get_stt_service()
        command = stt_service.process_text_command(request.text)

        if not command:
            return VoiceCommandResponse(
                action="unknown",
                message="No entendí el comando. Intenta decir: 'Kronos vamos a [destino]'",
                success=False,
            )

        # Buscar coordenadas del destino usando destinos frecuentes del usuario
        destination_coords = None
        if request.user_id and command["destination"]:
            try:
                from kronos.infrastructure.storage.user_storage import UserStorage

                storage = UserStorage()
                destinations = storage.get_frequent_destinations(request.user_id)

                # Buscar destino en destinos frecuentes
                for dest in destinations:
                    if dest["name"].lower() == command["destination"].lower():
                        destination_coords = {"lat": dest["lat"], "lng": dest["lng"]}
                        break

                # Si no se encuentra en destinos frecuentes, intentar geocodificación
                if not destination_coords:
                    # TODO: Implementar geocodificación con Nominatim u otro servicio
                    # Por ahora, retornar None
                    pass
            except Exception as e:
                print(f"Error al buscar destino: {e}")

        # Mensaje de confirmación
        if destination_coords:
            message = f"Entendido. Vamos a {command['destination']}."
        else:
            message = f"Voy a configurar ruta hacia {command['destination']}. ¿Puedes proporcionar las coordenadas?"

        return VoiceCommandResponse(
            action=command["action"],
            destination=command["destination"],
            destination_coords=destination_coords,
            message=message,
            success=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar comando: {str(e)}")


@router.post("/voice/command")
async def process_voice_command(
    audio: UploadFile = File(..., description="Archivo de audio con el comando"),
    user_id: Optional[str] = Form(None, description="ID del usuario"),
):
    """
    Procesa un comando de voz desde audio.

    Ejemplo: Audio diciendo "Kronos vamos a trabajo"

    Args:
        audio: Archivo de audio (MP3, WAV, etc.)
        user_id: ID del usuario (opcional)

    Returns:
        Respuesta con destino y acción
    """
    try:
        # Leer audio
        audio_data = await audio.read()

        # Por ahora, requerimos que el cliente haga STT
        # En el futuro, integrar Whisper o servicio STT real aquí
        return VoiceCommandResponse(
            action="pending",
            message="Por ahora, usa /voice/command/text con el texto del comando. STT desde audio será implementado próximamente.",
            success=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")


@router.get("/voice/command/test")
async def test_voice_command(
    text: str = "Kronos vamos a trabajo",
    user_id: Optional[str] = None,
):
    """
    Prueba un comando de voz (para testing).

    Args:
        text: Texto del comando
        user_id: ID del usuario (opcional)

    Returns:
        Respuesta del comando procesado
    """
    request = VoiceCommandRequest(text=text, user_id=user_id)
    return await process_voice_command_text(request)
