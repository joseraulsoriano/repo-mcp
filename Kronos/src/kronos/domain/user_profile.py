"""
Perfil de usuario.

Entidades relacionadas con el perfil y configuración del usuario.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from kronos.domain.entities import Position


@dataclass
class BikeSpecs:
    """Especificaciones técnicas de una motocicleta."""

    brand: str  # Marca (ej: Honda, Yamaha, etc.)
    model: str  # Modelo (ej: CBR 600, MT-07, etc.)
    year: Optional[int] = None  # Año
    engine_size: Optional[float] = None  # Cilindraje en cc
    max_speed: Optional[float] = None  # Velocidad máxima en km/h
    max_safe_accel: Optional[float] = None  # Aceleración máxima segura en m/s²
    bike_type: Literal["urban", "sport", "work", "adventure"] = "urban"


@dataclass
class UserProfile:
    """
    Perfil completo del usuario.

    Contiene información personal, ubicación, destino y motocicleta.
    """

    user_id: str  # Identificador único del usuario
    name: Optional[str] = None  # Nombre del usuario
    
    # Ubicación
    home_location: Optional[Position] = None  # Ubicación de casa/donde vive
    current_location: Optional[Position] = None  # Ubicación actual
    
    # Destino
    destination: Optional[Position] = None  # Destino del viaje
    destination_name: Optional[str] = None  # Nombre del destino (ej: "Trabajo", "Casa")
    
    # Motocicleta
    bike_specs: Optional[BikeSpecs] = None  # Especificaciones de la moto
    preferred_speed: Optional[float] = None  # Velocidad preferida en m/s
    
    # Preferencias
    risk_tolerance: float = 0.3  # Tolerancia al riesgo (0.0 - 1.0)
    voice_enabled: bool = True  # Activar notificaciones por voz
