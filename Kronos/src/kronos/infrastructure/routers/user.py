"""
Router de usuario y perfil.

Endpoints para gestión de perfil de usuario y configuración inicial.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from kronos.domain.entities import Position
from kronos.domain.user_profile import BikeSpecs, UserProfile
from kronos.infrastructure.services.bike_specs_service import BikeSpecsService
from kronos.infrastructure.services.welcome_service import WelcomeService
from kronos.infrastructure.storage.user_storage import UserStorage

router = APIRouter()

# Instancias globales
_bike_specs_service: Optional[BikeSpecsService] = None
_welcome_service: Optional[WelcomeService] = None
_user_storage: Optional[UserStorage] = None


def get_bike_specs_service() -> BikeSpecsService:
    """Obtiene el servicio de fichas técnicas."""
    global _bike_specs_service
    if _bike_specs_service is None:
        _bike_specs_service = BikeSpecsService()
    return _bike_specs_service


def get_welcome_service() -> WelcomeService:
    """Obtiene el servicio de bienvenida."""
    global _welcome_service
    if _welcome_service is None:
        _welcome_service = WelcomeService()
    return _welcome_service


def get_user_storage() -> UserStorage:
    """Obtiene el almacenamiento de usuarios."""
    global _user_storage
    if _user_storage is None:
        _user_storage = UserStorage()
    return _user_storage


class BikeInfoRequest(BaseModel):
    """Solicitud de información de moto."""

    brand: str  # Marca
    model: Optional[str] = None  # Modelo
    engine_size: Optional[float] = None  # Cilindraje en cc


class UserSetupRequest(BaseModel):
    """Solicitud de configuración inicial del usuario."""

    name: Optional[str] = None
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    destination_name: Optional[str] = None
    bike_brand: str
    bike_model: Optional[str] = None
    bike_engine_size: Optional[float] = None
    preferred_speed: Optional[float] = None  # km/h
    risk_tolerance: float = 0.3


class UserProfileResponse(BaseModel):
    """Respuesta de perfil de usuario."""

    user_id: str
    name: Optional[str] = None
    home_location: Optional[dict] = None
    destination: Optional[dict] = None
    destination_name: Optional[str] = None
    bike_specs: Optional[dict] = None
    preferred_speed: Optional[float] = None
    risk_tolerance: float = 0.3


@router.get("/welcome/audio")
async def get_welcome_audio():
    """
    Obtiene audio de bienvenida con voz neutral.

    Returns:
        Audio MP3 de bienvenida
    """
    from fastapi.responses import Response

    try:
        welcome_service = get_welcome_service()
        audio_data = welcome_service.get_welcome_audio()

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="kronos_welcome.mp3"',
                "Cache-Control": "no-cache",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar audio de bienvenida: {str(e)}")


@router.get("/welcome/message")
async def get_welcome_message():
    """
    Obtiene mensaje de bienvenida en texto.

    Returns:
        Mensaje de bienvenida
    """
    welcome_service = get_welcome_service()
    return {"message": welcome_service.get_welcome_message()}


@router.post("/bike/specs")
async def get_bike_specs(request: BikeInfoRequest):
    """
    Obtiene especificaciones técnicas de una moto.

    Args:
        request: Información de la moto (marca, modelo, cilindraje)

    Returns:
        Especificaciones técnicas de la moto
    """
    try:
        specs_service = get_bike_specs_service()
        specs = specs_service.search_bike(
            brand=request.brand, model=request.model, engine_size=request.engine_size
        )

        if not specs:
            raise HTTPException(status_code=404, detail="Moto no encontrada")

        return {
            "brand": specs.brand,
            "model": specs.model,
            "year": specs.year,
            "engine_size": specs.engine_size,
            "max_speed": specs.max_speed,
            "max_safe_accel": specs.max_safe_accel,
            "bike_type": specs.bike_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar moto: {str(e)}")


@router.get("/bike/specs")
async def get_bike_specs_get(
    brand: str = Query(..., description="Marca de la moto"),
    model: Optional[str] = Query(None, description="Modelo de la moto"),
    engine_size: Optional[float] = Query(None, description="Cilindraje en cc"),
):
    """
    Obtiene especificaciones técnicas de una moto (GET).

    Args:
        brand: Marca de la moto
        model: Modelo de la moto (opcional)
        engine_size: Cilindraje en cc (opcional)

    Returns:
        Especificaciones técnicas de la moto
    """
    try:
        specs_service = get_bike_specs_service()
        specs = specs_service.search_bike(brand=brand, model=model, engine_size=engine_size)

        if not specs:
            raise HTTPException(status_code=404, detail="Moto no encontrada")

        return {
            "brand": specs.brand,
            "model": specs.model,
            "year": specs.year,
            "engine_size": specs.engine_size,
            "max_speed": specs.max_speed,
            "max_safe_accel": specs.max_safe_accel,
            "bike_type": specs.bike_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar moto: {str(e)}")


@router.post("/user/setup")
async def setup_user(request: UserSetupRequest):
    """
    Configura el perfil inicial del usuario.

    Args:
        request: Datos de configuración inicial

    Returns:
        Perfil de usuario configurado
    """
    try:
        import uuid

        # Generar ID de usuario único
        user_id = str(uuid.uuid4())

        # Buscar especificaciones de la moto
        specs_service = get_bike_specs_service()
        bike_specs = specs_service.search_bike(
            brand=request.bike_brand,
            model=request.bike_model,
            engine_size=request.bike_engine_size,
        )

        # Crear ubicaciones
        home_location = None
        if request.home_lat and request.home_lng:
            home_location = Position(lat=request.home_lat, lng=request.home_lng)

        destination = None
        if request.destination_lat and request.destination_lng:
            destination = Position(lat=request.destination_lat, lng=request.destination_lng)

        # Convertir velocidad de km/h a m/s si se proporciona
        preferred_speed_ms = None
        if request.preferred_speed:
            preferred_speed_ms = request.preferred_speed / 3.6

        # Crear perfil
        profile = UserProfile(
            user_id=user_id,
            name=request.name,
            home_location=home_location,
            destination=destination,
            destination_name=request.destination_name,
            bike_specs=bike_specs,
            preferred_speed=preferred_speed_ms,
            risk_tolerance=request.risk_tolerance,
        )

        # Guardar perfil en almacenamiento
        storage = get_user_storage()
        storage.save_profile(profile)

        # Si hay destino, guardarlo como destino frecuente si tiene nombre
        if destination and request.destination_name:
            storage.add_frequent_destination(user_id, destination, request.destination_name)

        # Retornar perfil como respuesta
        return UserProfileResponse(
            user_id=profile.user_id,
            name=profile.name,
            home_location={"lat": home_location.lat, "lng": home_location.lng}
            if home_location
            else None,
            destination={"lat": destination.lat, "lng": destination.lng} if destination else None,
            destination_name=profile.destination_name,
            bike_specs={
                "brand": bike_specs.brand,
                "model": bike_specs.model,
                "engine_size": bike_specs.engine_size,
                "max_safe_accel": bike_specs.max_safe_accel,
                "bike_type": bike_specs.bike_type,
            }
            if bike_specs
            else None,
            preferred_speed=profile.preferred_speed,
            risk_tolerance=profile.risk_tolerance,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al configurar usuario: {str(e)}")


@router.get("/setup/audio")
async def get_setup_audio():
    """
    Obtiene audio de instrucciones para configuración inicial.

    Returns:
        Audio MP3 de instrucciones
    """
    from fastapi.responses import Response

    try:
        welcome_service = get_welcome_service()
        audio_data = welcome_service.get_setup_audio()

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="kronos_setup.mp3"',
                "Cache-Control": "no-cache",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar audio de configuración: {str(e)}")


@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    Obtiene el perfil de un usuario.

    Args:
        user_id: ID del usuario

    Returns:
        Perfil del usuario
    """
    try:
        storage = get_user_storage()
        profile = storage.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return UserProfileResponse(
            user_id=profile.user_id,
            name=profile.name,
            home_location={"lat": profile.home_location.lat, "lng": profile.home_location.lng}
            if profile.home_location
            else None,
            destination={"lat": profile.destination.lat, "lng": profile.destination.lng}
            if profile.destination
            else None,
            destination_name=profile.destination_name,
            bike_specs={
                "brand": profile.bike_specs.brand,
                "model": profile.bike_specs.model,
                "engine_size": profile.bike_specs.engine_size,
                "max_safe_accel": profile.bike_specs.max_safe_accel,
                "bike_type": profile.bike_specs.bike_type,
            }
            if profile.bike_specs
            else None,
            preferred_speed=profile.preferred_speed,
            risk_tolerance=profile.risk_tolerance,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener perfil: {str(e)}")


@router.get("/user/{user_id}/routes")
async def get_user_routes(user_id: str):
    """
    Obtiene las rutas guardadas de un usuario.

    Args:
        user_id: ID del usuario

    Returns:
        Lista de rutas del usuario
    """
    try:
        storage = get_user_storage()
        routes = storage.get_routes(user_id)
        return {"user_id": user_id, "routes": routes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener rutas: {str(e)}")


@router.post("/user/{user_id}/routes")
async def save_user_route(
    user_id: str,
    origin_lat: float = Query(..., description="Latitud de origen"),
    origin_lng: float = Query(..., description="Longitud de origen"),
    destination_lat: float = Query(..., description="Latitud de destino"),
    destination_lng: float = Query(..., description="Longitud de destino"),
    route_name: Optional[str] = Query(None, description="Nombre de la ruta"),
):
    """
    Guarda una ruta para un usuario.

    Args:
        user_id: ID del usuario
        origin_lat: Latitud de origen
        origin_lng: Longitud de origen
        destination_lat: Latitud de destino
        destination_lng: Longitud de destino
        route_name: Nombre de la ruta (opcional)

    Returns:
        Confirmación de guardado
    """
    try:
        storage = get_user_storage()
        origin = Position(lat=origin_lat, lng=origin_lng)
        destination = Position(lat=destination_lat, lng=destination_lng)

        storage.save_route(user_id, origin, destination, route_name)

        return {"status": "saved", "user_id": user_id, "route_name": route_name or "Ruta guardada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar ruta: {str(e)}")


@router.get("/user/{user_id}/destinations")
async def get_frequent_destinations(user_id: str):
    """
    Obtiene destinos frecuentes de un usuario.

    Args:
        user_id: ID del usuario

    Returns:
        Lista de destinos frecuentes
    """
    try:
        storage = get_user_storage()
        destinations = storage.get_frequent_destinations(user_id)
        return {"user_id": user_id, "destinations": destinations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener destinos frecuentes: {str(e)}")
