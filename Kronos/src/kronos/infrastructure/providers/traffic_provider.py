"""
Proveedores de datos de tráfico.

Estructura para integrar APIs de tráfico como Google Maps, Waze, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional

from kronos.domain.entities import Position, TrafficDensity


class TrafficProviderInterface(ABC):
    """Interfaz para proveedores de tráfico."""

    @abstractmethod
    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """Obtiene la densidad de tráfico en una posición."""

    @abstractmethod
    def get_traffic_info(self, position: Position) -> dict:
        """Obtiene información detallada de tráfico."""


class GoogleMapsTrafficProvider(TrafficProviderInterface):
    """
    Proveedor de tráfico usando Google Maps API.

    Requiere API key de Google Maps.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el proveedor de Google Maps.

        Args:
            api_key: API key de Google Maps (opcional)
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"

    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """
        Obtiene densidad de tráfico usando Google Maps.

        Args:
            position: Posición actual

        Returns:
            Densidad de tráfico
        """
        if not self.api_key:
            # Sin API key, retornar FREE por defecto
            return TrafficDensity.FREE

        try:
            # TODO: Implementar llamada a Google Maps Traffic API
            # Ejemplo de estructura:
            # response = requests.get(
            #     f"{self.base_url}/traffic/v1/flow",
            #     params={
            #         "key": self.api_key,
            #         "location": f"{position.lat},{position.lng}",
            #     }
            # )
            # data = response.json()
            # density = self._parse_density(data)
            # return density
            
            # Por ahora, retornar FREE
            return TrafficDensity.FREE
        except Exception:
            return TrafficDensity.FREE

    def get_traffic_info(self, position: Position) -> dict:
        """
        Obtiene información detallada de tráfico.

        Args:
            position: Posición actual

        Returns:
            Diccionario con información de tráfico
        """
        density = self.get_traffic_density(position)
        return {
            "density": density,
            "speed": None,  # Se obtendría de la API
            "incidents": [],  # Se obtendría de la API
        }

    def _parse_density(self, data: dict) -> TrafficDensity:
        """Parsea densidad desde respuesta de Google Maps."""
        # TODO: Implementar parsing según formato de Google Maps
        return TrafficDensity.FREE


class WazeTrafficProvider(TrafficProviderInterface):
    """
    Proveedor de tráfico usando Waze API (no oficial).

    Nota: Waze no tiene API pública oficial. Este proveedor
    sería para uso interno o con permisos especiales.
    """

    def __init__(self):
        """Inicializa el proveedor de Waze."""
        pass

    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """
        Obtiene densidad de tráfico usando Waze.

        Args:
            position: Posición actual

        Returns:
            Densidad de tráfico
        """
        # TODO: Implementar integración con Waze (requiere permisos especiales)
        return TrafficDensity.FREE

    def get_traffic_info(self, position: Position) -> dict:
        """
        Obtiene información detallada de tráfico.

        Args:
            position: Posición actual

        Returns:
            Diccionario con información de tráfico
        """
        density = self.get_traffic_density(position)
        return {
            "density": density,
            "speed": None,
            "incidents": [],
        }


class MockTrafficProviderWithPosition(TrafficProviderInterface):
    """
    Proveedor mock que simula densidad de tráfico basada en ubicación.

    Útil para pruebas con ubicaciones reales de Puebla.
    """

    def __init__(self):
        """Inicializa el proveedor mock."""
        # Zonas de Puebla con densidad simulada
        self.zones = {
            # Centro histórico (más tráfico)
            (19.04, 19.05, -98.21, -98.20): TrafficDensity.SLOW,
            # Ángelopolis (tráfico variable)
            (19.04, 19.06, -98.23, -98.22): TrafficDensity.FREE,
            # Cholula (tráfico moderado)
            (19.06, 19.07, -98.31, -98.30): TrafficDensity.SLOW,
        }

    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """
        Obtiene densidad simulada basada en zona de Puebla.

        Args:
            position: Posición actual

        Returns:
            Densidad de tráfico simulada
        """
        for (min_lat, max_lat, min_lng, max_lng), density in self.zones.items():
            if min_lat <= position.lat <= max_lat and min_lng <= position.lng <= max_lng:
                return density
        
        # Por defecto, tráfico libre
        return TrafficDensity.FREE

    def get_traffic_info(self, position: Position) -> dict:
        """
        Obtiene información de tráfico simulada.

        Args:
            position: Posición actual

        Returns:
            Diccionario con información de tráfico
        """
        density = self.get_traffic_density(position)
        return {
            "density": density,
            "speed": 50.0 if density == TrafficDensity.FREE else 30.0,  # km/h simulado
            "incidents": [],
        }
