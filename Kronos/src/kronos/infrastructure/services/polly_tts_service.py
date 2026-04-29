"""
Servicio de síntesis de voz usando AWS Polly.

AWS Polly tiene voces excelentes incluyendo "Mia" que suena muy similar a Alexa.
"""

import io
import os
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    POLLY_AVAILABLE = True
except ImportError:
    POLLY_AVAILABLE = False


class PollyTTSService:
    """
    Servicio TTS usando AWS Polly.

    Usa la voz "Mia" (español mexicano) que suena muy similar a Alexa.
    Requiere credenciales de AWS configuradas.
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        voice_id: str = "Mia",  # Voz similar a Alexa (español mexicano)
    ):
        """
        Inicializa el servicio Polly.

        Args:
            aws_access_key_id: AWS Access Key ID (opcional, usa env vars si no se proporciona)
            aws_secret_access_key: AWS Secret Access Key (opcional, usa env vars si no se proporciona)
            region_name: Región de AWS (default: us-east-1)
            voice_id: ID de voz de Polly (default: Mia - similar a Alexa)
        """
        if not POLLY_AVAILABLE:
            raise ImportError(
                "boto3 no está instalado. Instala con: pip install boto3"
            )

        # Obtener credenciales de variables de entorno si no se proporcionan
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.region_name = region_name
        self.voice_id = voice_id

        # Inicializar cliente Polly
        if self.aws_access_key_id and self.aws_secret_access_key:
            self.polly_client = boto3.client(
                "polly",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
        else:
            # Intentar usar credenciales por defecto de AWS (IAM role, ~/.aws/credentials, etc.)
            try:
                self.polly_client = boto3.client("polly", region_name=self.region_name)
            except Exception as e:
                raise ValueError(
                    f"No se pudieron configurar credenciales de AWS: {e}. "
                    "Configura AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY o usa aws configure."
                )

    def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Convierte texto a audio usando AWS Polly.

        Args:
            text: Texto a convertir
            voice_id: ID de voz (opcional, usa self.voice_id si no se especifica)

        Returns:
            Audio MP3 en bytes
        """
        voice = voice_id or self.voice_id

        try:
            # Sintetizar texto a voz
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice,
                Engine="neural",  # Usar motor neuronal para mejor calidad (similar a Alexa)
            )

            # Leer audio de la respuesta
            audio_stream = response["AudioStream"]
            audio_data = audio_stream.read()

            return audio_data

        except (ClientError, BotoCoreError) as e:
            raise Exception(f"Error al sintetizar voz con Polly: {str(e)}")

    def list_voices(self, language_code: str = "es-MX") -> list:
        """
        Lista voces disponibles en un idioma.

        Args:
            language_code: Código de idioma (ej: es-MX, es-ES)

        Returns:
            Lista de voces disponibles
        """
        try:
            response = self.polly_client.describe_voices(LanguageCode=language_code)
            return response["Voices"]
        except (ClientError, BotoCoreError) as e:
            raise Exception(f"Error al listar voces: {str(e)}")


# Voces disponibles en español mexicano
POLLY_VOICES_ES_MX = {
    "Mia": {
        "id": "Mia",
        "name": "Mia",
        "gender": "Female",
        "description": "Voz femenina mexicana, similar a Alexa",
        "neural": True,
    },
    "Lupe": {
        "id": "Lupe",
        "name": "Lupe",
        "gender": "Female",
        "description": "Voz femenina mexicana alternativa",
        "neural": True,
    },
    "Andres": {
        "id": "Andres",
        "name": "Andrés",
        "gender": "Male",
        "description": "Voz masculina mexicana",
        "neural": True,
    },
}


def get_polly_service_if_configured() -> Optional[PollyTTSService]:
    """
    Intenta obtener servicio Polly si está configurado.

    Returns:
        PollyTTSService si las credenciales están disponibles, None en caso contrario
    """
    if not POLLY_AVAILABLE:
        return None

    try:
        # Intentar crear servicio con credenciales disponibles
        return PollyTTSService()
    except (ValueError, Exception):
        # Si no hay credenciales, retornar None
        return None
