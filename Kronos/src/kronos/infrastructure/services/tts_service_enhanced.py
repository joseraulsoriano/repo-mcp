"""
Servicio de síntesis de voz mejorado.

Intentos de mejorar la calidad de voz usando diferentes técnicas.
Por ahora usa gTTS con optimizaciones, pero gTTS tiene limitaciones inherentes.
"""

import io
from typing import Optional

from gtts import gTTS
from pydantic import BaseModel


class EnhancedVoiceConfig(BaseModel):
    """Configuración de voz mejorada."""

    language: str = "es"
    slow: bool = True  # Hablar más lento suena más natural con gTTS
    tld: str = "com.mx"
    # Probar diferentes combinaciones


class EnhancedTTSService:
    """
    Servicio TTS con mejoras.

    gTTS tiene limitaciones - estas mejoras ayudan un poco,
    pero para voz realmente natural se necesita un servicio premium.
    """

    def __init__(self, config: Optional[EnhancedVoiceConfig] = None):
        """Inicializa el servicio mejorado."""
        self.config = config or EnhancedVoiceConfig()

    def text_to_speech(self, text: str) -> bytes:
        """
        Genera audio con configuración optimizada.

        Args:
            text: Texto a convertir

        Returns:
            Audio MP3
        """
        try:
            # gTTS funciona mejor con slow=True para sonar menos robótico
            tts = gTTS(
                text=text,
                lang=self.config.language,
                slow=self.config.slow,  # True ayuda a sonar más natural
                tld=self.config.tld,
            )

            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            return audio_buffer.read()

        except Exception as e:
            print(f"Error al generar audio mejorado: {e}")
            raise


class PremiumTTSService:
    """
    Servicio TTS para integración con servicios premium.

    Esta clase está preparada para usar servicios como:
    - Azure Text-to-Speech (voces neuronales muy naturales)
    - AWS Polly (buena calidad, acentos mexicanos)
    - ElevenLabs (ultra realista, de pago)

    Por ahora, es un placeholder para futura implementación.
    """

    def __init__(self, provider: str = "azure"):
        """
        Inicializa servicio premium.

        Args:
            provider: "azure", "polly", "elevenlabs"
        """
        self.provider = provider
        # TODO: Inicializar cliente según proveedor

    def text_to_speech(self, text: str, voice_name: Optional[str] = None) -> bytes:
        """
        Genera audio usando servicio premium.

        Args:
            text: Texto a convertir
            voice_name: Nombre de voz específica (opcional)

        Returns:
            Audio en bytes
        """
        # TODO: Implementar según proveedor
        # Ejemplo para Azure:
        # from azure.cognitiveservices.speech import SpeechSynthesizer
        # synthesizer = SpeechSynthesizer(...)
        # result = synthesizer.speak_text_async(text).get()
        # return result.audio_data

        raise NotImplementedError(
            "Servicio premium TTS requiere configuración de API keys. "
            "Por ahora, usa EnhancedTTSService con slow=True para mejor calidad."
        )


# Función helper para obtener el mejor servicio disponible
def get_best_tts_service():
    """
    Obtiene el mejor servicio TTS disponible.

    Intenta AWS Polly primero (similar a Alexa), luego usa enhanced con gTTS.

    Returns:
        Servicio TTS mejor disponible
    """
    # Intentar usar AWS Polly (similar a Alexa) si está configurado
    try:
        from kronos.infrastructure.services.polly_tts_service import (
            get_polly_service_if_configured,
        )

        polly_service = get_polly_service_if_configured()
        if polly_service:
            return polly_service
    except Exception:
        # Si Polly no está disponible, continuar con gTTS
        pass

    # Fallback a enhanced gTTS con slow=True
    return EnhancedTTSService(config=EnhancedVoiceConfig(slow=True, tld="com.mx"))
