"""
Proveedores de datos externos.

Interfaces y implementaciones para obtener datos
de GPS, tráfico, mapas, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional

from kronos.domain.entities import (
    LightState,
    Position,
    Signal,
    Signals,
    Traffic,
    TrafficDensity,
)


class GPSProvider(ABC):
    """Proveedor de datos GPS."""

    @abstractmethod
    def get_position(self) -> Position:
        """Obtiene la posición actual."""

    @abstractmethod
    def get_speed(self) -> float:
        """Obtiene la velocidad actual en m/s."""

    @abstractmethod
    def get_acceleration(self) -> float:
        """Obtiene la aceleración actual en m/s²."""


class TrafficProvider(ABC):
    """Proveedor de datos de tráfico."""

    @abstractmethod
    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """Obtiene la densidad de tráfico en una posición."""


class MapProvider(ABC):
    """Proveedor de datos de mapas."""

    @abstractmethod
    def get_next_signal(self, position: Position) -> Optional[Signal]:
        """Obtiene información del próximo semáforo."""

    @abstractmethod
    def get_following_signal(self, position: Position) -> Optional[Signal]:
        """Obtiene información del siguiente semáforo."""

    @abstractmethod
    def get_distance_remaining(self, position: Position, destination: Position) -> float:
        """Obtiene la distancia restante en metros."""


class MockGPSProvider(GPSProvider):
    """Proveedor GPS mock para desarrollo y testing."""

    def __init__(self, position: Optional[Position] = None, speed: float = 10.0, acceleration: float = 0.0):
        """Inicializa el proveedor mock."""
        self._position = position or Position(lat=0.0, lng=0.0)
        self._speed = speed
        self._acceleration = acceleration

    def get_position(self) -> Position:
        """Retorna la posición mock."""
        return self._position

    def get_speed(self) -> float:
        """Retorna la velocidad mock."""
        return self._speed

    def get_acceleration(self) -> float:
        """Retorna la aceleración mock."""
        return self._acceleration


class MockTrafficProvider(TrafficProvider):
    """Proveedor de tráfico mock para desarrollo y testing."""

    def __init__(self, density: TrafficDensity = TrafficDensity.FREE):
        """Inicializa el proveedor mock."""
        self._density = density

    def get_traffic_density(self, position: Position) -> TrafficDensity:
        """Retorna la densidad de tráfico mock."""
        return self._density


class MockMapProvider(MapProvider):
    """Proveedor de mapas mock para desarrollo y testing."""

    def __init__(
        self,
        next_signal: Optional[Signal] = None,
        following_signal: Optional[Signal] = None,
        distance_remaining: float = 1000.0,
    ):
        """Inicializa el proveedor mock."""
        self._next_signal = next_signal
        self._following_signal = following_signal
        self._distance_remaining = distance_remaining

    def get_next_signal(self, position: Position) -> Optional[Signal]:
        """Retorna el próximo semáforo mock."""
        return self._next_signal

    def get_following_signal(self, position: Position) -> Optional[Signal]:
        """Retorna el siguiente semáforo mock."""
        return self._following_signal

    def get_distance_remaining(self, position: Position, destination: Position) -> float:
        """Retorna la distancia restante mock."""
        return self._distance_remaining


# Re-exportar proveedores OSM
try:
    from kronos.infrastructure.providers.osm_provider import OSMProvider
except ImportError:
    # Si overpy no está instalado, OSMProvider no estará disponible
    OSMProvider = None  # type: ignore

# Re-exportar proveedores de tráfico
try:
    from kronos.infrastructure.providers.traffic_provider import (
        GoogleMapsTrafficProvider,
        MockTrafficProviderWithPosition,
        WazeTrafficProvider,
    )
except ImportError:
    GoogleMapsTrafficProvider = None  # type: ignore
    WazeTrafficProvider = None  # type: ignore
    MockTrafficProviderWithPosition = None  # type: ignore
