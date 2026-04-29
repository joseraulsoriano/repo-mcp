"""
Proveedor de mapas usando OpenStreetMap/Overpass API.

Obtiene datos reales de calles, semáforos y rutas.
"""

import time
from typing import Optional

import overpy
from geopy.distance import distance

from kronos.domain.entities import LightState, Position, Signal, TrafficDensity
from kronos.infrastructure.providers import MapProvider

# Radio de búsqueda en metros
SEARCH_RADIUS = 500  # 500 metros para buscar semáforos cercanos


class OSMProvider(MapProvider):
    """
    Proveedor de mapas usando OpenStreetMap.

    Utiliza Overpass API para obtener datos de calles y semáforos.
    """

    def __init__(self):
        """Inicializa el proveedor OSM."""
        self.api = overpy.Overpass()
        self._cache = {}  # Cache simple para evitar consultas repetidas
        self._cache_ttl = 300  # TTL de 5 minutos

    def _get_cache_key(self, position: Position, radius: int) -> str:
        """Genera clave de caché para una posición."""
        # Redondeamos a 3 decimales (aprox 100 metros)
        lat = round(position.lat, 3)
        lng = round(position.lng, 3)
        return f"{lat},{lng},{radius}"

    def _get_from_cache(self, key: str) -> Optional[dict]:
        """Obtiene datos del caché si están vigentes."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None

    def _save_to_cache(self, key: str, data: dict):
        """Guarda datos en el caché."""
        self._cache[key] = (data, time.time())

    def find_traffic_lights(self, position: Position, radius: int = SEARCH_RADIUS) -> list[dict]:
        """
        Encuentra semáforos cercanos usando Overpass API.

        Args:
            position: Posición actual
            radius: Radio de búsqueda en metros

        Returns:
            Lista de semáforos con información (distance, node_id, etc.)
        """
        cache_key = self._get_cache_key(position, radius)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get("traffic_lights", [])

        try:
            # Convertir radio a grados (aproximado: 1 grado ≈ 111 km)
            radius_deg = radius / 111000

            # Query Overpass para encontrar semáforos (traffic_signals)
            query = f"""
            [out:json][timeout:10];
            (
              node["highway"="traffic_signals"](around:{radius},{position.lat},{position.lng});
              way["highway"="traffic_signals"](around:{radius},{position.lat},{position.lng});
            );
            out body;
            """
            
            result = self.api.query(query)
            
            traffic_lights = []
            for node in result.nodes:
                node_lat = float(node.lat)
                node_lng = float(node.lon)
                
                # Calcular distancia real en metros
                node_pos = Position(lat=node_lat, lng=node_lng)
                dist = self._calculate_distance(position, node_pos)
                
                traffic_lights.append({
                    "id": node.id,
                    "lat": node_lat,
                    "lng": node_lng,
                    "distance": dist,
                    "tags": node.tags,
                })
            
            # Ordenar por distancia
            traffic_lights.sort(key=lambda x: x["distance"])
            
            # Guardar en caché
            self._save_to_cache(cache_key, {"traffic_lights": traffic_lights})
            
            return traffic_lights

        except Exception as e:
            # Si falla la consulta, retornar lista vacía
            print(f"Error al consultar OSM: {e}")
            return []

    def get_next_signal(self, position: Position) -> Optional[Signal]:
        """
        Obtiene el próximo semáforo en la ruta.

        Args:
            position: Posición actual

        Returns:
            Información del próximo semáforo o None
        """
        traffic_lights = self.find_traffic_lights(position)
        
        if not traffic_lights:
            return None
        
        # Tomar el más cercano
        nearest = traffic_lights[0]
        
        # Estado del semáforo (OSM no tiene estado en tiempo real, usar default)
        # En producción, esto vendría de una API de tráfico o sensores
        state = LightState.GREEN  # Por defecto
        
        # Tiempo restante estimado basado en ciclo típico de semáforos
        # (esto es una aproximación, en producción usar datos reales)
        remaining_time = None
        
        return Signal(
            distance=nearest["distance"],
            state=state,
            remaining_time=remaining_time,
        )

    def get_following_signal(self, position: Position) -> Optional[Signal]:
        """
        Obtiene el siguiente semáforo después del próximo.

        Args:
            position: Posición actual

        Returns:
            Información del siguiente semáforo o None
        """
        traffic_lights = self.find_traffic_lights(position, radius=1000)  # Buscar más lejos
        
        if len(traffic_lights) < 2:
            return None
        
        # Tomar el segundo más cercano
        second = traffic_lights[1]
        
        state = LightState.GREEN  # Por defecto
        remaining_time = None
        
        return Signal(
            distance=second["distance"],
            state=state,
            remaining_time=remaining_time,
        )

    def get_distance_remaining(self, position: Position, destination: Position) -> float:
        """
        Calcula la distancia restante usando geopy.

        Args:
            position: Posición actual
            destination: Destino

        Returns:
            Distancia en metros
        """
        try:
            dist = distance((position.lat, position.lng), (destination.lat, destination.lng))
            return dist.meters
        except Exception:
            # Fallback a cálculo simple si geopy falla
            return self._calculate_distance(position, destination)

    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """
        Calcula distancia usando fórmula de Haversine.

        Args:
            pos1: Posición 1
            pos2: Posición 2

        Returns:
            Distancia en metros
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371000  # Radio de la Tierra en metros
        lat1, lon1 = radians(pos1.lat), radians(pos1.lng)
        lat2, lon2 = radians(pos2.lat), radians(pos2.lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get_route_info(self, position: Position, destination: Position) -> dict:
        """
        Obtiene información de la ruta usando OSM.

        Args:
            position: Posición actual
            destination: Destino

        Returns:
            Diccionario con información de la ruta
        """
        distance_remaining = self.get_distance_remaining(position, destination)
        
        # Contar semáforos en la ruta (simplificado: buscar en línea recta)
        # En producción, esto debería usar routing real
        midpoint = Position(
            lat=(position.lat + destination.lat) / 2,
            lng=(position.lng + destination.lng) / 2,
        )
        route_distance = distance_remaining
        search_radius = min(route_distance / 2, 2000)  # Máximo 2km
        
        traffic_lights = self.find_traffic_lights(midpoint, radius=int(search_radius))
        
        return {
            "distance": distance_remaining,
            "traffic_lights_count": len(traffic_lights),
            "estimated_time_minutes": None,  # Se calcularía con velocidad
        }
