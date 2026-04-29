"""
Configuración compartida para tests.
"""

import pytest
from unittest.mock import Mock

from kronos.domain.entities import Position, User, UserState, Bike, Motion, Traffic, TrafficDensity
from kronos.infrastructure.providers import GPSProvider, TrafficProvider, MapProvider


@pytest.fixture
def sample_position():
    """Posición de prueba (Centro de Puebla)."""
    return Position(lat=19.0425, lng=-98.1981)


@pytest.fixture
def sample_user():
    """Usuario de prueba."""
    return User(state=UserState.ON_TIME, risk_tolerance=0.3)


@pytest.fixture
def sample_bike():
    """Moto de prueba."""
    return Bike(type="urban", max_safe_accel=2.5)


@pytest.fixture
def sample_motion():
    """Movimiento de prueba."""
    return Motion(speed=13.89, acceleration=0.0)  # ~50 km/h


@pytest.fixture
def mock_gps_provider():
    """Proveedor GPS mock."""
    provider = Mock(spec=GPSProvider)
    provider.get_position.return_value = Position(lat=19.0425, lng=-98.1981)
    provider.get_speed.return_value = 13.89
    provider.get_acceleration.return_value = 0.0
    return provider


@pytest.fixture
def mock_traffic_provider():
    """Proveedor de tráfico mock."""
    provider = Mock(spec=TrafficProvider)
    provider.get_traffic_density.return_value = TrafficDensity.FREE
    return provider


@pytest.fixture
def mock_map_provider():
    """Proveedor de mapas mock."""
    provider = Mock(spec=MapProvider)
    provider.get_next_signal.return_value = None
    provider.get_following_signal.return_value = None
    provider.get_distance_remaining.return_value = 1000.0
    return provider
