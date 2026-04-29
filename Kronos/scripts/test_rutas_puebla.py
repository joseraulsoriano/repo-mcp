#!/usr/bin/env python3
"""
Script de prueba de rutas en Puebla.

Prueba rutas entre lugares conocidos de Puebla,
detectando semáforos y calculando tiempos estimados.
"""

import json
import sys
from pathlib import Path

import requests

# Lugares conocidos de Puebla con coordenadas exactas
PUEBLA_LUGARES = {
    "centro": {
        "name": "Centro Histórico de Puebla (Zócalo)",
        "lat": 19.0425,
        "lng": -98.1981,
        "description": "Plaza principal del centro histórico",
    },
    "angelopolis": {
        "name": "Plaza Ángelopolis",
        "lat": 19.0500,
        "lng": -98.2267,
        "description": "Centro comercial y zona residencial moderna",
    },
    "cholula": {
        "name": "Cholula Centro",
        "lat": 19.0631,
        "lng": -98.3033,
        "description": "Centro de Cholula, cerca de la pirámide",
    },
    "ufp": {
        "name": "Universidad de las Américas Puebla (UDLAP)",
        "lat": 19.0408,
        "lng": -98.2231,
        "description": "Universidad en San Andrés Cholula",
    },
    "hospital": {
        "name": "Hospital del Niño Poblano",
        "lat": 19.0589,
        "lng": -98.2300,
        "description": "Hospital principal en zona sur",
    },
    "terminal": {
        "name": "Terminal CAPU (Central de Autobuses)",
        "lat": 19.0736,
        "lng": -98.2217,
        "description": "Terminal principal de autobuses",
    },
}

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Imprime un título de sección."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Imprime un subtítulo."""
    print(f"\n--- {title} ---")


def get_decision(lat: float, lng: float, speed: float = 13.89, use_osm: bool = True):
    """
    Obtiene una decisión del API.

    Args:
        lat: Latitud
        lng: Longitud
        speed: Velocidad en m/s
        use_osm: Usar OpenStreetMap

    Returns:
        Decisión del API o None si hay error
    """
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/decisions",
            params={"lat": lat, "lng": lng, "speed": speed, "use_osm": use_osm},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Error al obtener decisión: {e}")
        return None


def print_location_info(lugar: dict):
    """Imprime información de un lugar."""
    print(f"\n📍 {lugar['name']}")
    print(f"   Coordenadas: {lugar['lat']}, {lugar['lng']}")
    print(f"   {lugar['description']}")


def print_decision_info(decision: dict):
    """Imprime información de una decisión."""
    print(f"\n✅ Decisión: {decision['decision']}")
    print(f"   Modo: {decision['mode']}")
    print(f"   Mensaje: {decision['message']}")
    print(f"   Riesgo: {decision['risk_score']:.2f} ({decision['risk_level']})")
    print(f"   Confianza: {decision['confidence']:.2f}")
    if decision.get("position"):
        pos = decision["position"]
        print(f"   Posición procesada: {pos['lat']}, {pos['lng']}")


def calculate_route_time(distance_m: float, speed_ms: float) -> dict:
    """
    Calcula tiempo estimado de ruta.

    Args:
        distance_m: Distancia en metros
        speed_ms: Velocidad en m/s

    Returns:
        Diccionario con tiempos estimados
    """
    if speed_ms <= 0:
        return {"minutes": 0, "seconds": 0, "hours": 0}

    time_seconds = distance_m / speed_ms
    hours = int(time_seconds // 3600)
    minutes = int((time_seconds % 3600) // 60)
    seconds = int(time_seconds % 60)

    return {
        "total_seconds": time_seconds,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcula distancia entre dos puntos usando fórmula de Haversine.

    Args:
        lat1, lng1: Coordenadas del punto 1
        lat2, lng2: Coordenadas del punto 2

    Returns:
        Distancia en metros
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Radio de la Tierra en metros
    lat1, lon1 = radians(lat1), radians(lng1)
    lat2, lon2 = radians(lat2), radians(lng2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def test_route(origen: str, destino: str, velocidad_kmh: float = 50):
    """
    Prueba una ruta entre dos lugares.

    Args:
        origen: Nombre del lugar de origen
        destino: Nombre del lugar de destino
        velocidad_kmh: Velocidad en km/h
    """
    if origen not in PUEBLA_LUGARES or destino not in PUEBLA_LUGARES:
        print(f"✗ Lugares no encontrados: {origen} -> {destino}")
        return False

    origen_data = PUEBLA_LUGARES[origen]
    destino_data = PUEBLA_LUGARES[destino]

    # Convertir velocidad de km/h a m/s
    velocidad_ms = velocidad_kmh / 3.6

    # Calcular distancia
    distancia_m = calculate_distance(
        origen_data["lat"], origen_data["lng"], destino_data["lat"], destino_data["lng"]
    )
    distancia_km = distancia_m / 1000

    # Calcular tiempo estimado
    tiempo_info = calculate_route_time(distancia_m, velocidad_ms)

    print_subsection(f"Ruta: {origen_data['name']} → {destino_data['name']}")

    print(f"\n📏 Distancia: {distancia_km:.2f} km ({distancia_m:.0f} m)")
    print(f"🚗 Velocidad: {velocidad_kmh} km/h ({velocidad_ms:.2f} m/s)")
    
    if tiempo_info["hours"] > 0:
        print(f"⏱️  Tiempo estimado: {tiempo_info['hours']}h {tiempo_info['minutes']}min")
    else:
        print(f"⏱️  Tiempo estimado: {tiempo_info['minutes']}min {tiempo_info['seconds']}sec")

    # Probar origen
    print(f"\n🔵 Origen: {origen_data['name']}")
    decision_origen = get_decision(origen_data["lat"], origen_data["lng"], velocidad_ms)
    if decision_origen:
        print_decision_info(decision_origen)

    # Probar destino
    print(f"\n🔴 Destino: {destino_data['name']}")
    decision_destino = get_decision(destino_data["lat"], destino_data["lng"], velocidad_ms)
    if decision_destino:
        print_decision_info(decision_destino)

    # Probar con POST incluyendo destino
    print(f"\n🔄 Ruta completa (POST con destino)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/decisions",
            json={
                "lat": origen_data["lat"],
                "lng": origen_data["lng"],
                "speed": velocidad_ms,
                "destination_lat": destino_data["lat"],
                "destination_lng": destino_data["lng"],
                "use_osm": True,
            },
            timeout=30,
        )
        response.raise_for_status()
        decision_ruta = response.json()
        print_decision_info(decision_ruta)
    except Exception as e:
        print(f"✗ Error: {e}")

    return True


def test_single_location(lugar_key: str, velocidad_kmh: float = 50):
    """
    Prueba una ubicación individual.

    Args:
        lugar_key: Clave del lugar
        velocidad_kmh: Velocidad en km/h
    """
    if lugar_key not in PUEBLA_LUGARES:
        print(f"✗ Lugar no encontrado: {lugar_key}")
        return False

    lugar = PUEBLA_LUGARES[lugar_key]
    velocidad_ms = velocidad_kmh / 3.6

    print_location_info(lugar)

    # Probar con OSM
    print("\n🌐 Con OpenStreetMap (use_osm=true):")
    decision_osm = get_decision(lugar["lat"], lugar["lng"], velocidad_ms, use_osm=True)
    if decision_osm:
        print_decision_info(decision_osm)

    # Probar sin OSM (mock)
    print("\n📦 Sin OpenStreetMap (use_osm=false):")
    decision_mock = get_decision(lugar["lat"], lugar["lng"], velocidad_ms, use_osm=False)
    if decision_mock:
        print_decision_info(decision_mock)

    return True


def list_locations():
    """Lista todos los lugares disponibles."""
    print_section("Lugares Disponibles para Pruebas")
    for key, lugar in PUEBLA_LUGARES.items():
        print(f"\n  [{key}] {lugar['name']}")
        print(f"       {lugar['description']}")
        print(f"       Coordenadas: {lugar['lat']}, {lugar['lng']}")


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Prueba rutas en Puebla con Kronos")
    parser.add_argument(
        "--origen", type=str, help="Lugar de origen (centro, angelopolis, cholula, etc.)"
    )
    parser.add_argument(
        "--destino", type=str, help="Lugar de destino (centro, angelopolis, cholula, etc.)"
    )
    parser.add_argument("--lugar", type=str, help="Probar un lugar específico")
    parser.add_argument("--velocidad", type=float, default=50, help="Velocidad en km/h (default: 50)")
    parser.add_argument("--list", action="store_true", help="Listar lugares disponibles")
    parser.add_argument(
        "--all-routes",
        action="store_true",
        help="Probar todas las rutas principales",
    )

    args = parser.parse_args()

    print_section("Pruebas de Rutas en Puebla - Kronos")

    # Verificar que el servicio esté disponible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"\n⚠ El servicio no está disponible (código: {response.status_code})")
            print(f"  Asegúrate de que esté corriendo: docker-compose up -d")
            sys.exit(1)
    except Exception as e:
        print(f"\n⚠ El servicio no está disponible: {e}")
        print(f"  Asegúrate de que esté corriendo: docker-compose up -d")
        sys.exit(1)

    print("✓ Servicio disponible\n")

    if args.list:
        list_locations()
        sys.exit(0)

    if args.lugar:
        test_single_location(args.lugar, args.velocidad)
        sys.exit(0)

    if args.origen and args.destino:
        test_route(args.origen, args.destino, args.velocidad)
        sys.exit(0)

    if args.all_routes:
        # Rutas principales a probar
        rutas = [
            ("centro", "angelopolis", "Centro → Ángelopolis"),
            ("centro", "cholula", "Centro → Cholula"),
            ("centro", "ufp", "Centro → UDLAP"),
            ("angelopolis", "cholula", "Ángelopolis → Cholula"),
            ("centro", "terminal", "Centro → CAPU"),
        ]

        print_section("Probando Todas las Rutas Principales")

        for origen, destino, nombre in rutas:
            test_route(origen, destino, args.velocidad)
            print("\n" + "-" * 70)

        sys.exit(0)

    # Si no se especifica nada, mostrar ayuda
    print("\nUso:")
    print("  --list                 : Listar lugares disponibles")
    print("  --lugar <key>          : Probar un lugar específico")
    print("  --origen <key> --destino <key> : Probar una ruta")
    print("  --all-routes           : Probar todas las rutas principales")
    print("  --velocidad <km/h>     : Velocidad en km/h (default: 50)")
    print("\nEjemplos:")
    print("  python scripts/test_rutas_puebla.py --list")
    print("  python scripts/test_rutas_puebla.py --lugar centro")
    print("  python scripts/test_rutas_puebla.py --origen centro --destino angelopolis")
    print("  python scripts/test_rutas_puebla.py --all-routes --velocidad 60")


if __name__ == "__main__":
    main()
