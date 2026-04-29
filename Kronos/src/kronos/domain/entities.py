"""
Entidades del dominio.

Representan los conceptos fundamentales del sistema
sin dependencias externas.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional


class UserState(str, Enum):
    """Estado del usuario respecto a su hora objetivo."""

    ON_TIME = "ON_TIME"
    LATE = "LATE"
    CRITICAL = "CRITICAL"


class TrafficDensity(str, Enum):
    """Densidad de tráfico."""

    FREE = "FREE"
    SLOW = "SLOW"
    BLOCKED = "BLOCKED"


class LightState(str, Enum):
    """Estado de un semáforo."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class RiskLevel(str, Enum):
    """Nivel de riesgo categorico."""

    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class DecisionAction(str, Enum):
    """Acción recomendada por el sistema."""

    PROCEED = "PROCEED"
    WAIT = "WAIT"
    HOLD = "HOLD"
    FILTER_ALLOWED = "FILTER_ALLOWED"
    FILTER_FORBIDDEN = "FILTER_FORBIDDEN"


class DecisionMode(str, Enum):
    """Modo de operación de la decisión."""

    NORMAL = "NORMAL"
    SAFE = "SAFE"


@dataclass
class Position:
    """Posición geográfica."""

    lat: float
    lng: float


@dataclass
class Motion:
    """Datos de movimiento actual."""

    speed: float  # m/s
    acceleration: float  # m/s²


@dataclass
class Bike:
    """Información de la motocicleta."""

    type: Literal["urban", "sport", "work"]
    max_safe_accel: float  # m/s²


@dataclass
class Route:
    """Información de la ruta."""

    distance_remaining: float  # metros
    time_remaining: int  # minutos


@dataclass
class Traffic:
    """Información de tráfico."""

    density: TrafficDensity


@dataclass
class Signal:
    """Información de un semáforo."""

    distance: float  # metros
    state: LightState
    remaining_time: Optional[int] = None  # segundos


@dataclass
class Signals:
    """Información de semáforos en la ruta."""

    next_light: Signal
    following_light: Optional[Signal] = None


@dataclass
class User:
    """Información del usuario."""

    state: UserState
    risk_tolerance: float  # 0.0 - 1.0


@dataclass
class ContextSnapshot:
    """
    Snapshoot completo del contexto para evaluar decisiones.

    Contiene todos los datos necesarios para que el Policy Engine
    pueda evaluar políticas y generar decisiones.
    """

    user: User
    position: Position
    motion: Motion
    bike: Bike
    route: Route
    traffic: Traffic
    signals: Signals
    confidence: float  # 0.0 - 1.0


@dataclass
class RiskScore:
    """Puntuación de riesgo de una acción."""

    value: float  # 0.0 - 1.0
    level: RiskLevel

    @classmethod
    def from_value(cls, value: float) -> "RiskScore":
        """Crea un RiskScore desde un valor numérico."""
        if value < 0.0 or value > 1.0:
            raise ValueError(f"Risk value must be between 0.0 and 1.0, got {value}")

        if value < 0.33:
            level = RiskLevel.LOW
        elif value < 0.66:
            level = RiskLevel.MED
        else:
            level = RiskLevel.HIGH

        return cls(value=value, level=level)


@dataclass
class Decision:
    """
    Decisión generada por el Policy Engine.

    Representa el resultado de evaluar todas las políticas
    relevantes sobre un ContextSnapshot.
    """

    action: DecisionAction
    mode: DecisionMode
    risk_score: RiskScore
    message: str
    confidence: float  # 0.0 - 1.0
