"""
Servicio de fichas técnicas de motocicletas.

Consulta especificaciones técnicas de motos para configurar
el perfil del usuario automáticamente.
"""

from typing import Optional

from kronos.domain.user_profile import BikeSpecs


class BikeSpecsService:
    """
    Servicio para consultar fichas técnicas de motocicletas.

    Usa una base de datos local de motos comunes para obtener
    especificaciones automáticamente.
    """

    def __init__(self):
        """Inicializa el servicio con base de datos de motos."""
        # Base de datos local de motos comunes en México/Puebla
        # En producción, esto podría venir de una API o base de datos real
        self.bikes_db = {
            # Honda
            ("honda", "cbr", "600"): BikeSpecs(
                brand="Honda",
                model="CBR 600",
                bike_type="sport",
                max_speed=280.0,  # km/h
                max_safe_accel=4.5,  # m/s²
                engine_size=600.0,
            ),
            ("honda", "cb", "500"): BikeSpecs(
                brand="Honda",
                model="CB 500",
                bike_type="urban",
                max_speed=180.0,
                max_safe_accel=3.5,
                engine_size=500.0,
            ),
            ("honda", "cbf", "150"): BikeSpecs(
                brand="Honda",
                model="CBF 150",
                bike_type="urban",
                max_speed=110.0,
                max_safe_accel=2.5,
                engine_size=150.0,
            ),
            # Yamaha
            ("yamaha", "mt", "07"): BikeSpecs(
                brand="Yamaha",
                model="MT-07",
                bike_type="urban",
                max_speed=200.0,
                max_safe_accel=4.0,
                engine_size=689.0,
            ),
            ("yamaha", "r3"): BikeSpecs(
                brand="Yamaha",
                model="R3",
                bike_type="sport",
                max_speed=180.0,
                max_safe_accel=3.8,
                engine_size=321.0,
            ),
            # Kawasaki
            ("kawasaki", "ninja", "300"): BikeSpecs(
                brand="Kawasaki",
                model="Ninja 300",
                bike_type="sport",
                max_speed=190.0,
                max_safe_accel=3.6,
                engine_size=296.0,
            ),
            # Bajaj
            ("bajaj", "pulsar", "150"): BikeSpecs(
                brand="Bajaj",
                model="Pulsar 150",
                bike_type="urban",
                max_speed=115.0,
                max_safe_accel=2.3,
                engine_size=150.0,
            ),
            # Italika
            ("italika", "ft", "150"): BikeSpecs(
                brand="Italika",
                model="FT 150",
                bike_type="urban",
                max_speed=100.0,
                max_safe_accel=2.0,
                engine_size=150.0,
            ),
            # KTM
            ("ktm", "duke", "200"): BikeSpecs(
                brand="KTM",
                model="Duke 200",
                bike_type="urban",
                max_speed=140.0,
                max_safe_accel=3.0,
                engine_size=199.5,
            ),
        }

    def search_bike(
        self, brand: str, model: Optional[str] = None, engine_size: Optional[float] = None
    ) -> Optional[BikeSpecs]:
        """
        Busca especificaciones de una moto.

        Args:
            brand: Marca de la moto (ej: "honda", "yamaha")
            model: Modelo de la moto (opcional, ej: "cbr", "mt")
            engine_size: Cilindraje en cc (opcional)

        Returns:
            Especificaciones de la moto o None si no se encuentra
        """
        brand_lower = brand.lower().strip()

        # Buscar por marca y modelo
        if model:
            model_lower = model.lower().strip()
            # Intentar varios formatos de búsqueda
            search_keys = [
                (brand_lower, model_lower),
                (brand_lower, model_lower, str(int(engine_size)) if engine_size else None),
            ]

            for key in search_keys:
                # Limpiar None
                clean_key = tuple(k for k in key if k is not None)
                if len(clean_key) == 2:
                    # Buscar coincidencias parciales
                    for db_key, specs in self.bikes_db.items():
                        if (
                            clean_key[0] in db_key[0].lower()
                            and clean_key[1] in " ".join(db_key[1:]).lower()
                        ):
                            # Actualizar engine_size si se proporciona
                            if engine_size:
                                specs.engine_size = engine_size
                            return specs
                elif clean_key in self.bikes_db:
                    specs = self.bikes_db[clean_key]
                    if engine_size:
                        specs.engine_size = engine_size
                    return specs

        # Si solo se proporciona marca, buscar la más común
        matching = [
            specs for key, specs in self.bikes_db.items() if brand_lower in key[0].lower()
        ]
        if matching:
            # Retornar la primera coincidencia
            specs = matching[0]
            if engine_size:
                specs.engine_size = engine_size
            return specs

        # Si no se encuentra, crear especificaciones por defecto
        return self._create_default_specs(brand, model, engine_size)

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
