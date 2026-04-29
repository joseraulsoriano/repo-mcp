"""
Servicio de fichas técnicas de motos usando MCP (Model Context Protocol).

Busca información de motos en línea en lugar de tenerla guardada localmente.
"""

from typing import Optional

from kronos.domain.user_profile import BikeSpecs


class BikeSpecsMCPService:
    """
    Servicio de fichas técnicas usando MCP para búsqueda web.

    Busca especificaciones de motos en línea cuando no están
    en la base de datos local.
    """

    def __init__(self, local_service=None):
        """
        Inicializa el servicio MCP.

        Args:
            local_service: Servicio local como fallback
        """
        self.local_service = local_service

    def search_bike(
        self, brand: str, model: Optional[str] = None, engine_size: Optional[float] = None
    ) -> Optional[BikeSpecs]:
        """
        Busca especificaciones de una moto usando MCP.

        Primero intenta base de datos local, luego busca en línea.

        Args:
            brand: Marca de la moto
            model: Modelo de la moto (opcional)
            engine_size: Cilindraje en cc (opcional)

        Returns:
            Especificaciones de la moto o None si no se encuentra
        """
        # Primero intentar base de datos local
        if self.local_service:
            local_result = self.local_service.search_bike(brand, model, engine_size)
            if local_result and local_result.model != "Unknown":
                return local_result

        # Si no se encuentra localmente, usar MCP para buscar en línea
        # Nota: Esto requiere implementación de MCP client
        # Por ahora, retornar especificaciones por defecto
        return self._create_default_specs(brand, model, engine_size)

    def search_online(
        self, brand: str, model: Optional[str] = None, engine_size: Optional[float] = None
    ) -> Optional[BikeSpecs]:
        """
        Busca especificaciones en línea usando MCP/web search.

        Args:
            brand: Marca de la moto
            model: Modelo de la moto
            engine_size: Cilindraje en cc

        Returns:
            Especificaciones encontradas o None
        """
        # TODO: Implementar búsqueda web usando MCP
        # Ejemplo de query:
        # "Honda CBR 600 ficha técnica especificaciones máximo velocidad aceleración"
        
        # Por ahora, retornar None (se usará default)
        return None

    def _create_default_specs(
        self, brand: str, model: Optional[str], engine_size: Optional[float]
    ) -> BikeSpecs:
        """
        Crea especificaciones por defecto para una moto no encontrada.

        Args:
            brand: Marca de la moto
            model: Modelo de la moto
            engine_size: Cilindraje en cc

        Returns:
            Especificaciones por defecto
        """
        # Determinar tipo de moto basado en cilindraje si está disponible
        if engine_size:
            if engine_size >= 500:
                bike_type = "sport"
                max_safe_accel = 4.0
                max_speed = 200.0
            elif engine_size >= 250:
                bike_type = "urban"
                max_safe_accel = 3.0
                max_speed = 150.0
            else:
                bike_type = "urban"
                max_safe_accel = 2.5
                max_speed = 120.0
        else:
            # Valores por defecto conservadores
            bike_type = "urban"
            max_safe_accel = 2.5
            max_speed = 120.0

        return BikeSpecs(
            brand=brand.title(),
            model=model.title() if model else "Unknown",
            bike_type=bike_type,
            engine_size=engine_size or 150.0,
            max_speed=max_speed,
            max_safe_accel=max_safe_accel,
        )
