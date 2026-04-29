"""
Dependencias de la aplicación.

Container de dependencias para inyección en FastAPI.
"""

from typing import Optional

from kronos.application.services import (
    ContextAssembler,
    DecisionService,
    PolicyEngine,
    RiskEvaluator,
)
from kronos.domain.entities import Position
from kronos.domain.policies import FilteringPolicy, SignalsPolicy, TrafficPolicy
from kronos.infrastructure.providers import (
    GPSProvider,
    MapProvider,
    MockGPSProvider,
    MockMapProvider,
    MockTrafficProvider,
    OSMProvider,
    TrafficProvider,
)

# Importar proveedores de tráfico opcionales
try:
    from kronos.infrastructure.providers.traffic_provider import MockTrafficProviderWithPosition
except ImportError:
    MockTrafficProviderWithPosition = None  # type: ignore

# Instancias globales (en producción usar inyección de dependencias apropiada)
_gps_provider: GPSProvider | None = None
_traffic_provider: TrafficProvider | None = None
_map_provider: MapProvider | None = None
_decision_service: DecisionService | None = None


def get_gps_provider() -> GPSProvider:
    """Obtiene el proveedor GPS."""
    global _gps_provider
    if _gps_provider is None:
        _gps_provider = MockGPSProvider()
    return _gps_provider


def get_traffic_provider() -> TrafficProvider:
    """Obtiene el proveedor de tráfico."""
    global _traffic_provider
    if _traffic_provider is None:
        _traffic_provider = MockTrafficProvider()
    return _traffic_provider


def get_map_provider() -> MapProvider:
    """Obtiene el proveedor de mapas."""
    global _map_provider
    if _map_provider is None:
        _map_provider = MockMapProvider()
    return _map_provider


def get_decision_service() -> DecisionService:
    """Obtiene el servicio de decisión."""
    global _decision_service
    if _decision_service is None:
        # Crear políticas
        policies = [
            SignalsPolicy(),
            FilteringPolicy(),
            TrafficPolicy(),
        ]

        # Crear servicios
        context_assembler = ContextAssembler(
            gps_provider=get_gps_provider(),
            traffic_provider=get_traffic_provider(),
            map_provider=get_map_provider(),
        )

        risk_evaluator = RiskEvaluator()
        policy_engine = PolicyEngine(policies=policies)

        _decision_service = DecisionService(
            context_assembler=context_assembler,
            risk_evaluator=risk_evaluator,
            policy_engine=policy_engine,
        )

    return _decision_service


def create_decision_service_with_location(
    position: Position,
    speed: Optional[float] = None,
    acceleration: Optional[float] = None,
    destination: Optional[Position] = None,
    use_osm: bool = False,
    user_id: Optional[str] = None,
) -> DecisionService:
    """
    Crea un servicio de decisión con ubicación específica.

    Args:
        position: Posición geográfica actual
        speed: Velocidad en m/s (opcional, default: 10.0)
        acceleration: Aceleración en m/s² (opcional, default: 0.0)
        destination: Destino (opcional)
        use_osm: Si True, usa OSMProvider para datos reales (default: False)

    Returns:
        Servicio de decisión configurado
    """
    # Crear proveedores con ubicación específica
    gps_provider = MockGPSProvider(
        position=position,
        speed=speed if speed is not None else 10.0,
        acceleration=acceleration if acceleration is not None else 0.0,
    )

    # Usar proveedor de tráfico con posición si está disponible
    if MockTrafficProviderWithPosition:
        traffic_provider = MockTrafficProviderWithPosition()
    else:
        traffic_provider = MockTrafficProvider()

    # Usar OSM si está disponible y se solicita
    if use_osm and OSMProvider:
        try:
            map_provider = OSMProvider()
            # Si hay destino, configurar distancia
            if destination:
                distance = map_provider.get_distance_remaining(position, destination)
                # Crear MockMapProvider con distancia calculada pero usar OSM para semáforos
                # Por ahora usamos OSM directamente
        except Exception as e:
            print(f"Error al inicializar OSMProvider, usando mock: {e}")
            map_provider = MockMapProvider()
            if destination:
                # Calcular distancia aproximada en metros
                from math import radians, sin, cos, sqrt, atan2

                R = 6371000
                lat1, lon1 = radians(position.lat), radians(position.lng)
                lat2, lon2 = radians(destination.lat), radians(destination.lng)
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = R * c
                map_provider._distance_remaining = distance
    else:
        map_provider = MockMapProvider()
        # Si hay destino, calcular distancia
        if destination:
            # Calcular distancia aproximada en metros (fórmula de Haversine simplificada)
            from math import radians, sin, cos, sqrt, atan2

            R = 6371000  # Radio de la Tierra en metros
            lat1, lon1 = radians(position.lat), radians(position.lng)
            lat2, lon2 = radians(destination.lat), radians(destination.lng)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            map_provider._distance_remaining = distance

    # Intentar obtener perfil del usuario si se proporciona user_id
    user_profile = None
    if user_id:
        try:
            from kronos.infrastructure.storage.user_storage import UserStorage

            storage = UserStorage()
            user_profile = storage.get_profile(user_id)
            if user_profile:
                # Usar velocidad preferida del usuario si no se especifica
                if speed is None and user_profile.preferred_speed:
                    speed = user_profile.preferred_speed
        except Exception as e:
            # Si falla, continuar sin perfil
            print(f"Error al obtener perfil de usuario: {e}")
            pass

    # Crear servicios
    context_assembler = ContextAssembler(
        gps_provider=gps_provider,
        traffic_provider=traffic_provider,
        map_provider=map_provider,
        user_profile=user_profile,
    )

    risk_evaluator = RiskEvaluator()
    
    policies = [
        SignalsPolicy(),
        FilteringPolicy(),
        TrafficPolicy(),
    ]
    policy_engine = PolicyEngine(policies=policies)

    return DecisionService(
        context_assembler=context_assembler,
        risk_evaluator=risk_evaluator,
        policy_engine=policy_engine,
    )
