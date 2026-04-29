"""
Servicio de bienvenida.

Mensajes de bienvenida y voz neutral para Kronos.
"""

from kronos.infrastructure.services.tts_service import TTSService, VoiceConfig
from kronos.infrastructure.services.tts_service_enhanced import (
    EnhancedTTSService,
    EnhancedVoiceConfig,
    get_best_tts_service,
)
from kronos.infrastructure.services.polly_tts_service import (
    PollyTTSService,
    get_polly_service_if_configured,
)


class WelcomeService:
    """
    Servicio de bienvenida con voz mejorada.

    Usa servicio TTS mejorado con slow=True para sonar más natural.
    gTTS tiene limitaciones inherentes - para voz realmente natural,
    se necesita un servicio premium (Azure TTS, AWS Polly, ElevenLabs).
    """

    def __init__(self):
        """Inicializa el servicio de bienvenida."""
        # Intentar usar AWS Polly (similar a Alexa) si está configurado
        # Si no, usar gTTS mejorado con slow=True
        try:
            # Primero intentar Polly (voz similar a Alexa)
            polly_service = get_polly_service_if_configured()
            if polly_service:
                self.tts_service = polly_service
                print("✓ Usando AWS Polly (voz similar a Alexa)")
                return
        except Exception:
            pass

        # Fallback a servicio mejorado con gTTS
        try:
            self.tts_service = get_best_tts_service()
            print("✓ Usando gTTS mejorado (slow=True)")
        except Exception:
            # Fallback final a servicio básico
            self.tts_config = VoiceConfig(
                language="es",
                slow=True,
                tld="com.mx",
            )
            self.tts_service = TTSService(config=self.tts_config)
            print("✓ Usando gTTS básico")

    def get_welcome_message(self) -> str:
        """
        Obtiene mensaje de bienvenida.

        Returns:
            Mensaje de bienvenida en texto
        """
        return "Bienvenido a Kronos. Tu asistente inteligente para motociclistas urbanos. Voy a ayudarte a llegar seguro a tu destino."

    def get_welcome_audio(self) -> bytes:
        """
        Genera audio de bienvenida con voz neutral.

        Returns:
            Audio MP3 de bienvenida
        """
        message = self.get_welcome_message()
        return self.tts_service.text_to_speech(message)

    def get_setup_message(self) -> str:
        """
        Obtiene mensaje para configuración inicial.

        Returns:
            Mensaje de configuración en texto
        """
        return "Antes de comenzar, necesito algunos datos. ¿Dónde estás ahora? ¿A dónde vas? ¿Qué tipo de motocicleta tienes?"

    def get_setup_audio(self) -> bytes:
        """
        Genera audio de configuración inicial.

        Returns:
            Audio MP3 de configuración
        """
        message = self.get_setup_message()
        return self.tts_service.text_to_speech(message)
