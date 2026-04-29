"""
Servicio de reconocimiento de voz (Speech-to-Text).

Convierte audio a texto para procesar comandos de voz.
"""

import io
import re
from typing import Optional, Tuple

# Nota: Para producción, considerar usar Whisper, Google Speech-to-Text,
# o Azure Speech Services para mejor calidad


class STTService:
    """
    Servicio de reconocimiento de voz.

    Convierte audio a texto para procesar comandos.
    Por ahora, usa una implementación simple basada en patrón.
    En producción, debería usar un servicio real de STT (Whisper, Google, Azure).
    """

    def __init__(self):
        """Inicializa el servicio STT."""
        # Patrones comunes de comandos
        self.command_patterns = {
            "vamos_a": re.compile(
                r"(?:kronos|vamos|ir|viajar|conducir|ir a|vamos a)\s+(?:a|hacia|para)?\s*([^\.\?!]+)",
                re.IGNORECASE,
            ),
            "destino": re.compile(
                r"(?:trabajo|casa|hogar|universidad|escuela|oficina|centro|ángel|cholula)",
                re.IGNORECASE,
            ),
        }

    def process_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Procesa audio y extrae texto.

        Nota: Esta es una implementación simplificada.
        En producción, usar Whisper o servicios de STT reales.

        Args:
            audio_data: Audio en bytes (formato MP3/WAV)

        Returns:
            Texto transcrito o None si no se puede procesar
        """
        # TODO: Integrar Whisper o servicio STT real
        # Por ahora, retornamos None para indicar que necesita implementación
        return None

    def process_text_command(self, text: str) -> Optional[dict]:
        """
        Procesa un comando de texto (después de STT).

        Extrae destino y acción del comando.

        Args:
            text: Texto del comando (ej: "Kronos vamos a trabajo")

        Returns:
            Dict con comando procesado o None si no se reconoce
        """
        text_lower = text.lower().strip()

        # Buscar patrón "vamos a [destino]"
        match = self.command_patterns["vamos_a"].search(text)
        if match:
            destination_text = match.group(1).strip()
            
            # Normalizar destinos comunes
            destination_normalized = self._normalize_destination(destination_text)
            
            return {
                "action": "navigate",
                "destination": destination_normalized,
                "original_text": text,
                "confidence": 0.8,
            }

        return None

    def _normalize_destination(self, destination: str) -> str:
        """
        Normaliza nombres de destinos comunes.

        Args:
            destination: Texto del destino

        Returns:
            Nombre normalizado del destino
        """
        destination_lower = destination.lower().strip()
        
        # Mapeo de variaciones a nombres estándar
        destination_map = {
            "trabajo": "trabajo",
            "oficina": "trabajo",
            "office": "trabajo",
            "casa": "casa",
            "hogar": "casa",
            "home": "casa",
            "universidad": "universidad",
            "uni": "universidad",
            "escuela": "universidad",
            "centro": "centro",
            "centro histórico": "centro",
            "zócalo": "centro",
            "ángel": "angelopolis",
            "angelopolis": "angelopolis",
            "plaza ángel": "angelopolis",
            "cholula": "cholula",
            "san pedro cholula": "cholula",
        }

        # Buscar coincidencia exacta o parcial
        for key, value in destination_map.items():
            if key in destination_lower:
                return value

        # Si no hay coincidencia, retornar original
        return destination

    def extract_destination_from_text(self, text: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Extrae destino y acción de un texto.

        Args:
            text: Texto del comando

        Returns:
            Tuple (destino_normalizado, nombre_original) o None
        """
        command = self.process_text_command(text)
        if command:
            return (command["destination"], command.get("original_text"))
        return None
