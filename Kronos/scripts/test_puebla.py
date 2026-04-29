#!/usr/bin/env python3
"""
Script de prueba para Puebla, México.

Prueba el servicio Kronos con ubicaciones reales de Puebla.
"""

import json
import sys
from pathlib import Path

import requests

# Coordenadas de Puebla
PUEBLA_COORDINATES = {
    "centro": {"lat": 19.0414, "lng": -98.2063, "name": "Centro de Puebla"},
    "angelopolis": {"lat": 19.0500, "lng": -98.2267, "name": "Ángelopolis"},
    "cholula": {"lat": 19.0631, "lng": -98.3033, "name": "Cholula"},
}

BASE_URL = "http://localhost:8000"


def test_location(lat: float, lng: float, name: str, speed: float = 13.89):
    """
    Prueba una ubicación específica.

    Args:
        lat: Latitud
        lng: Longitud
        name: Nombre de la ubicación
        speed: Velocidad en m/s (default: 50 km/h = 13.89 m/s)
    """
    print(f"\n{'='*60}")
    print(f"Probando ubicación: {name}")
    print(f"Coordenadas: {lat}, {lng}")
    print(f"Velocidad: {speed} m/s ({speed * 3.6:.1f} km/h)")
    print(f"{'='*60}")

    # Prueba GET con query parameters
    print("\n[GET] /api/v1/decisions")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/decisions",
            params={"lat": lat, "lng": lng, "speed": speed},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Estado: {response.status_code}")
        print(f"  Decisión: {data['decision']}")
        print(f"  Mensaje: {data['message']}")
        print(f"  Riesgo: {data['risk_score']:.2f} ({data['risk_level']})")
        print(f"  Confianza: {data['confidence']:.2f}")
        if data.get("position"):
            print(f"  Posición: {data['position']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Prueba POST con body
    print("\n[POST] /api/v1/decisions")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/decisions",
            json={"lat": lat, "lng": lng, "speed": speed},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Estado: {response.status_code}")
        print(f"  Decisión: {data['decision']}")
        print(f"  Mensaje: {data['message']}")
        print(f"  Riesgo: {data['risk_score']:.2f} ({data['risk_level']})")
        print(f"  Confianza: {data['confidence']:.2f}")
        if data.get("position"):
            print(f"  Posición: {data['position']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    return True


def test_health():
    """Prueba el endpoint de salud."""
    print("\n[GET] /health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Estado: {response.status_code}")
        print(f"  {data}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print("Pruebas de Kronos - Puebla, México")
    print("=" * 60)

    # Verificar que el servicio esté corriendo
    if not test_health():
        print("\n⚠ El servicio no está disponible. ¿Está corriendo?")
        print(f"  Intenta: docker-compose up -d")
        print(f"  O verifica que esté en: {BASE_URL}")
        sys.exit(1)

    # Probar ubicaciones de Puebla
    results = []
    for location in PUEBLA_COORDINATES.values():
        success = test_location(
            lat=location["lat"],
            lng=location["lng"],
            name=location["name"],
            speed=13.89,  # 50 km/h
        )
        results.append((location["name"], success))

    # Resumen
    print("\n" + "=" * 60)
    print("Resumen:")
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")

    all_ok = all(success for _, success in results)
    if all_ok:
        print("\n✓ Todas las pruebas pasaron")
        sys.exit(0)
    else:
        print("\n✗ Algunas pruebas fallaron")
        sys.exit(1)


if __name__ == "__main__":
    main()
