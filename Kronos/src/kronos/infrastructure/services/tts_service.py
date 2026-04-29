"""
Servicio de síntesis de voz (Text-to-Speech).

Convierte mensajes de texto del Policy Engine a audio
para dar indicaciones por voz al motociclista.
"""

import io
from typing import Optional

from gtts import gTTS
from pydantic import BaseModel


class VoiceConfig(BaseModel):
    """Configuración de voz."""

    language: str = "es"  # Código de idioma (es = español)
    slow: bool = False  # Hablar más lento
    tld: str = "com.mx"  # Top-level domain para acento (com.mx=mexicano, es=español)
    # Nota: gTTS usa voces sintéticas que pueden sonar robóticas
    # Para voces más naturales, considerar servicios como Azure TTS, AWS Polly, o ElevenLabs


class TTSService:
    """
    Servicio de síntesis de voz usando Google Text-to-Speech.

    Convierte mensajes de texto a audio MP3.
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        """
        Inicializa el servicio TTS.

        Args:
            config: Configuración de voz (opcional)
        """
        self.config = config or VoiceConfig()

    def text_to_speech(self, text: str, language: Optional[str] = None) -> bytes:
        """
        Convierte texto a audio.

        Args:
            text: Texto a convertir
            language: Código de idioma (opcional, usa config si no se especifica)

        Returns:
            Audio en formato MP3 como bytes
        """
        lang = language or self.config.language

        try:
            # Crear objeto gTTS
            tts = gTTS(text=text, lang=lang, slow=self.config.slow, tld=self.config.tld)

            # Generar audio en memoria
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            return audio_buffer.read()

        except Exception as e:
            # Si falla gTTS, retornar None para manejar error
            print(f"Error al generar audio: {e}")
            raise

    def generate_decision_audio(self, message: str, decision: str = "") -> bytes:
        """
        Genera audio para una decisión del Policy Engine.

        Args:
            message: Mensaje de la decisión
            decision: Tipo de decisión (opcional, se puede incluir en el mensaje)

        Returns:
            Audio en formato MP3 como bytes
        """
        # Formatear mensaje para voz
        # Los mensajes deben ser claros y concisos para voz
        voice_message = self._format_for_voice(message, decision)

        return self.text_to_speech(voice_message)

    def _format_for_voice(self, message: str, decision: str = "") -> str:
        """
        Formatea mensaje para voz.

        Hace ajustes para que el mensaje sea claro al escucharlo.

        Args:
            message: Mensaje original
            decision: Tipo de decisión

        Returns:
            Mensaje formateado para voz
        """
        # Limpiar mensaje para voz
        # Eliminar caracteres especiales que no se pronuncian bien
        voice_message = message

        # Reemplazar abreviaciones comunes
        replacements = {
            "km/h": "kilómetros por hora",
            "m/s": "metros por segundo",
            "°C": "grados centígrados",
            "...": ".",
            "  ": " ",  # Múltiples espacios a uno
        }

        for old, new in replacements.items():
            voice_message = voice_message.replace(old, new)

        # Asegurar que termina con punto
        if not voice_message.endswith((".", "!", "?")):
            voice_message += "."

        # Capitalizar primera letra
        voice_message = voice_message.capitalize()

        return voice_message
