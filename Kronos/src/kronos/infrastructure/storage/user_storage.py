"""
Almacenamiento de perfiles de usuario y rutas.

Persistencia de datos de usuario usando archivos JSON (temporal).
En producción, esto debería usar una base de datos real.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from kronos.domain.entities import Position
from kronos.domain.user_profile import BikeSpecs, UserProfile


class UserStorage:
    """
    Almacenamiento de perfiles de usuario y rutas.

    Usa archivos JSON para persistencia simple.
    En producción, usar MongoDB o PostgreSQL.
    """

    def __init__(self, storage_path: str = "/tmp/kronos_users.json"):
        """
        Inicializa el almacenamiento.

        Args:
            storage_path: Ruta del archivo JSON para almacenar datos
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Asegura que el archivo de almacenamiento exista."""
        if not self.storage_path.exists():
            self._write_data({})

    def _read_data(self) -> dict:
        """Lee datos del archivo."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_data(self, data: dict):
        """Escribe datos al archivo."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_profile(self, profile: UserProfile) -> bool:
        """
        Guarda un perfil de usuario.

        Args:
            profile: Perfil a guardar

        Returns:
            True si se guardó correctamente
        """
        try:
            data = self._read_data()
            
            # Convertir perfil a dict para almacenamiento
            profile_dict = {
                "user_id": profile.user_id,
                "name": profile.name,
                "home_location": {
                    "lat": profile.home_location.lat,
                    "lng": profile.home_location.lng,
                }
                if profile.home_location
                else None,
                "destination": {
                    "lat": profile.destination.lat,
                    "lng": profile.destination.lng,
                }
                if profile.destination
                else None,
                "destination_name": profile.destination_name,
                "bike_specs": {
                    "brand": profile.bike_specs.brand,
                    "model": profile.bike_specs.model,
                    "engine_size": profile.bike_specs.engine_size,
                    "max_safe_accel": profile.bike_specs.max_safe_accel,
                    "bike_type": profile.bike_specs.bike_type,
                }
                if profile.bike_specs
                else None,
                "preferred_speed": profile.preferred_speed,
                "risk_tolerance": profile.risk_tolerance,
                "voice_enabled": profile.voice_enabled,
            }

            # Inicializar usuarios si no existe
            if "users" not in data:
                data["users"] = {}

            data["users"][profile.user_id] = profile_dict
            self._write_data(data)
            return True
        except Exception as e:
            print(f"Error al guardar perfil: {e}")
            return False

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Obtiene un perfil de usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Perfil del usuario o None si no se encuentra
        """
        try:
            data = self._read_data()
            if "users" not in data or user_id not in data["users"]:
                return None

            profile_dict = data["users"][user_id]

            # Reconstruir perfil desde dict
            home_location = None
            if profile_dict.get("home_location"):
                home_location = Position(
                    lat=profile_dict["home_location"]["lat"],
                    lng=profile_dict["home_location"]["lng"],
                )

            destination = None
            if profile_dict.get("destination"):
                destination = Position(
                    lat=profile_dict["destination"]["lat"],
                    lng=profile_dict["destination"]["lng"],
                )

            bike_specs = None
            if profile_dict.get("bike_specs"):
                bs = profile_dict["bike_specs"]
                bike_specs = BikeSpecs(
                    brand=bs["brand"],
                    model=bs["model"],
                    engine_size=bs.get("engine_size"),
                    max_safe_accel=bs.get("max_safe_accel"),
                    bike_type=bs.get("bike_type", "urban"),
                )

            return UserProfile(
                user_id=profile_dict["user_id"],
                name=profile_dict.get("name"),
                home_location=home_location,
                destination=destination,
                destination_name=profile_dict.get("destination_name"),
                bike_specs=bike_specs,
                preferred_speed=profile_dict.get("preferred_speed"),
                risk_tolerance=profile_dict.get("risk_tolerance", 0.3),
                voice_enabled=profile_dict.get("voice_enabled", True),
            )
        except Exception as e:
            print(f"Error al obtener perfil: {e}")
            return None

    def save_route(self, user_id: str, origin: Position, destination: Position, route_name: Optional[str] = None):
        """
        Guarda una ruta asociada a un usuario.

        Args:
            user_id: ID del usuario
            origin: Posición de origen
            destination: Posición de destino
            route_name: Nombre de la ruta (opcional, ej: "Trabajo", "Casa")
        """
        try:
            data = self._read_data()

            # Inicializar rutas si no existe
            if "routes" not in data:
                data["routes"] = {}

            if user_id not in data["routes"]:
                data["routes"][user_id] = []

            route = {
                "origin": {"lat": origin.lat, "lng": origin.lng},
                "destination": {"lat": destination.lat, "lng": destination.lng},
                "name": route_name or f"Ruta {len(data['routes'][user_id]) + 1}",
            }

            data["routes"][user_id].append(route)
            self._write_data(data)
        except Exception as e:
            print(f"Error al guardar ruta: {e}")

    def get_routes(self, user_id: str) -> List[dict]:
        """
        Obtiene todas las rutas de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de rutas del usuario
        """
        try:
            data = self._read_data()
            if "routes" not in data or user_id not in data["routes"]:
                return []
            return data["routes"][user_id]
        except Exception as e:
            print(f"Error al obtener rutas: {e}")
            return []

    def add_frequent_destination(self, user_id: str, position: Position, name: str):
        """
        Agrega un destino frecuente a un usuario.

        Args:
            user_id: ID del usuario
            position: Posición del destino
            name: Nombre del destino (ej: "Trabajo", "Casa")
        """
        try:
            data = self._read_data()

            # Inicializar destinos frecuentes si no existe
            if "frequent_destinations" not in data:
                data["frequent_destinations"] = {}

            if user_id not in data["frequent_destinations"]:
                data["frequent_destinations"][user_id] = []

            destination = {
                "name": name,
                "lat": position.lat,
                "lng": position.lng,
            }

            # Evitar duplicados
            destinations = data["frequent_destinations"][user_id]
            if not any(
                d["name"] == name and d["lat"] == position.lat and d["lng"] == position.lng
                for d in destinations
            ):
                destinations.append(destination)
                self._write_data(data)
        except Exception as e:
            print(f"Error al agregar destino frecuente: {e}")

    def get_frequent_destinations(self, user_id: str) -> List[dict]:
        """
        Obtiene destinos frecuentes de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de destinos frecuentes
        """
        try:
            data = self._read_data()
            if "frequent_destinations" not in data or user_id not in data["frequent_destinations"]:
                return []
            return data["frequent_destinations"][user_id]
        except Exception as e:
            print(f"Error al obtener destinos frecuentes: {e}")
            return []
