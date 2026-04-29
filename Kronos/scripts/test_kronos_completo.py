#!/usr/bin/env python3
"""
Script de pruebas completo para Kronos.

Prueba movimiento entre lugares en Puebla, semáforos, reducción de tiempo
y todas las características del sistema.
"""

import json
import sys
import time
from typing import Dict, List, Optional

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Lugares en Puebla para pruebas
LUGARES_PUEBLA = {
    "centro": {
        "nombre": "Centro Histórico (Zócalo)",
        "lat": 19.0425,
        "lng": -98.1981,
        "descripcion": "Zócalo de Puebla",
    },
    "angelopolis": {
        "nombre": "Plaza Ángelopolis",
        "lat": 19.0500,
        "lng": -98.2267,
        "descripcion": "Centro comercial moderno",
    },
    "cholula": {
        "nombre": "Cholula Centro",
        "lat": 19.0631,
        "lng": -98.3033,
        "descripcion": "Centro de Cholula",
    },
    "udlap": {
        "nombre": "Universidad UDLAP",
        "lat": 19.0408,
        "lng": -98.2231,
        "descripcion": "Universidad",
    },
    "hospital_nino": {
        "nombre": "Hospital del Niño",
        "lat": 19.0589,
        "lng": -98.2300,
        "descripcion": "Hospital zona sur",
    },
    "terminal_capu": {
        "nombre": "Terminal CAPU",
        "lat": 19.0736,
        "lng": -98.2217,
        "descripcion": "Terminal de autobuses",
    },
}

# Rutas para probar
RUTAS_PRUEBA = [
    {
        "origen": "centro",
        "destino": "angelopolis",
        "descripcion": "Centro → Ángelopolis (zona comercial)",
        "velocidad_kmh": 50,
    },
    {
        "origen": "centro",
        "destino": "cholula",
        "descripcion": "Centro → Cholula (ruta larga)",
        "velocidad_kmh": 60,
    },
    {
        "origen": "centro",
        "destino": "udlap",
        "descripcion": "Centro → UDLAP (zona universitaria)",
        "velocidad_kmh": 45,
    },
    {
        "origen": "angelopolis",
        "destino": "hospital_nino",
        "descripcion": "Ángelopolis → Hospital (zona sur)",
        "velocidad_kmh": 40,
    },
]


def calcular_distancia(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcula distancia en metros usando fórmula de Haversine."""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Radio de la Tierra en metros
    lat1_rad, lon1_rad = radians(lat1), radians(lng1)
    lat2_rad, lon2_rad = radians(lat2), radians(lng2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def test_decision(lat: float, lng: float, speed_ms: float, use_osm: bool = True) -> Dict:
    """Prueba una decisión en una ubicación."""
    try:
        response = requests.get(
            f"{BASE_URL}/decisions",
            params={
                "lat": lat,
                "lng": lng,
                "speed": speed_ms,
                "use_osm": use_osm,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def test_decision_con_destino(
    origen: Dict, destino: Dict, speed_ms: float, use_osm: bool = True
) -> Dict:
    """Prueba una decisión con destino."""
    try:
        response = requests.post(
            f"{BASE_URL}/decisions",
            json={
                "lat": origen["lat"],
                "lng": origen["lng"],
                "speed": speed_ms,
                "destination_lat": destino["lat"],
                "destination_lng": destino["lng"],
                "use_osm": use_osm,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def analizar_decision(decision: Dict) -> Dict:
    """Analiza una decisión y extrae características."""
    if "error" in decision:
        return {"error": decision["error"]}

    return {
        "accion": decision.get("decision"),
        "modo": decision.get("mode"),
        "riesgo_score": decision.get("risk_score"),
        "riesgo_nivel": decision.get("risk_level"),
        "mensaje": decision.get("message"),
        "confianza": decision.get("confidence"),
        "posicion": decision.get("position"),
    }


def test_ruta_completa(ruta: Dict) -> Dict:
    """Prueba una ruta completa entre dos lugares."""
    origen_key = ruta["origen"]
    destino_key = ruta["destino"]

    if origen_key not in LUGARES_PUEBLA or destino_key not in LUGARES_PUEBLA:
        return {"error": f"Lugares no encontrados: {origen_key} o {destino_key}"}

    origen = LUGARES_PUEBLA[origen_key]
    destino = LUGARES_PUEBLA[destino_key]

    # Calcular distancia
    distancia_m = calcular_distancia(
        origen["lat"], origen["lng"], destino["lat"], destino["lng"]
    )
    distancia_km = distancia_m / 1000

    # Convertir velocidad de km/h a m/s
    velocidad_ms = ruta["velocidad_kmh"] / 3.6

    # Tiempo estimado sin filtrado (normal)
    tiempo_normal_min = (distancia_km / ruta["velocidad_kmh"]) * 60

    print(f"\n{'='*70}")
    print(f"RUTA: {ruta['descripcion']}")
    print(f"{'='*70}")
    print(f"Origen: {origen['nombre']} ({origen['lat']}, {origen['lng']})")
    print(f"Destino: {destino['nombre']} ({destino['lat']}, {destino['lng']})")
    print(f"Distancia: {distancia_km:.2f} km ({distancia_m:.0f} m)")
    print(f"Velocidad: {ruta['velocidad_kmh']} km/h ({velocidad_ms:.2f} m/s)")
    print(f"Tiempo estimado (normal): {tiempo_normal_min:.1f} minutos")

    # Probar decisión en origen
    print(f"\n📍 DECISIÓN EN ORIGEN:")
    decision_origen = test_decision(origen["lat"], origen["lng"], velocidad_ms, use_osm=True)
    analisis_origen = analizar_decision(decision_origen)
    
    if "error" not in analisis_origen:
        print(f"  Acción: {analisis_origen['accion']}")
        print(f"  Modo: {analisis_origen['modo']}")
        print(f"  Riesgo: {analisis_origen['riesgo_score']:.2f} ({analisis_origen['riesgo_nivel']})")
        print(f"  Mensaje: {analisis_origen['mensaje']}")
        print(f"  Confianza: {analisis_origen['confianza']:.2f}")
    else:
        print(f"  ❌ Error: {analisis_origen['error']}")

    # Probar decisión con destino (ruta completa)
    print(f"\n🛣️  DECISIÓN CON DESTINO (RUTA COMPLETA):")
    decision_ruta = test_decision_con_destino(origen, destino, velocidad_ms, use_osm=True)
    analisis_ruta = analizar_decision(decision_ruta)

    if "error" not in analisis_ruta:
        print(f"  Acción: {analisis_ruta['accion']}")
        print(f"  Modo: {analisis_ruta['modo']}")
        print(f"  Riesgo: {analisis_ruta['riesgo_score']:.2f} ({analisis_ruta['riesgo_nivel']})")
        print(f"  Mensaje: {analisis_ruta['mensaje']}")
        print(f"  Confianza: {analisis_ruta['confianza']:.2f}")

        # Análisis de reducción de tiempo potencial
        if analisis_ruta["accion"] == "FILTER_ALLOWED":
            # Si se permite filtrar, estimar reducción de tiempo
            tiempo_filtrado_min = tiempo_normal_min * 0.8  # 20% reducción estimada
            reduccion_min = tiempo_normal_min - tiempo_filtrado_min
            print(f"\n  ⏱️  REDUCCIÓN DE TIEMPO ESTIMADA:")
            print(f"     Tiempo normal: {tiempo_normal_min:.1f} min")
            print(f"     Tiempo con filtrado: {tiempo_filtrado_min:.1f} min")
            print(f"     Reducción: {reduccion_min:.1f} min ({reduccion_min/tiempo_normal_min*100:.1f}%)")
        elif analisis_ruta["accion"] == "FILTER_FORBIDDEN":
            print(f"\n  ⏱️  FILTRADO NO PERMITIDO")
            print(f"     Motivo: No se gana tiempo suficiente o riesgo alto")
    else:
        print(f"  ❌ Error: {analisis_ruta['error']}")

    # Probar decisión en destino
    print(f"\n🎯 DECISIÓN EN DESTINO:")
    decision_destino = test_decision(destino["lat"], destino["lng"], velocidad_ms, use_osm=True)
    analisis_destino = analizar_decision(decision_destino)

    if "error" not in analisis_destino:
        print(f"  Acción: {analisis_destino['accion']}")
        print(f"  Modo: {analisis_destino['modo']}")
        print(f"  Riesgo: {analisis_destino['riesgo_score']:.2f} ({analisis_destino['riesgo_nivel']})")
        print(f"  Mensaje: {analisis_destino['mensaje']}")
    else:
        print(f"  ❌ Error: {analisis_destino['error']}")

    return {
        "ruta": ruta["descripcion"],
        "distancia_km": distancia_km,
        "tiempo_estimado_min": tiempo_normal_min,
        "decision_origen": analisis_origen,
        "decision_ruta": analisis_ruta,
        "decision_destino": analisis_destino,
    }


def test_semaforos():
    """Prueba detección de semáforos en lugares conocidos."""
    print(f"\n{'='*70}")
    print("PRUEBA DE DETECCIÓN DE SEMÁFOROS")
    print(f"{'='*70}")

    lugares_test = ["centro", "angelopolis"]

    for lugar_key in lugares_test:
        lugar = LUGARES_PUEBLA[lugar_key]
        print(f"\n📍 {lugar['nombre']}:")

        decision = test_decision(lugar["lat"], lugar["lng"], 13.89, use_osm=True)
        analisis = analizar_decision(decision)

        if "error" not in analisis:
            print(f"  Semáforos detectados: {'Sí' if analisis['confianza'] > 0.7 else 'No'}")
            print(f"  Mensaje: {analisis['mensaje']}")
        else:
            print(f"  ❌ Error: {analisis['error']}")


def test_movimiento_simulado():
    """Simula movimiento entre lugares verificando decisiones."""
    print(f"\n{'='*70}")
    print("SIMULACIÓN DE MOVIMIENTO ENTRE LUGARES")
    print(f"{'='*70}")

    # Simular movimiento Centro → Ángelopolis
    origen = LUGARES_PUEBLA["centro"]
    destino = LUGARES_PUEBLA["angelopolis"]
    velocidad_ms = 13.89  # ~50 km/h

    # Calcular puntos intermedios (simplificado)
    pasos = 5
    lat_step = (destino["lat"] - origen["lat"]) / pasos
    lng_step = (destino["lng"] - origen["lng"]) / pasos

    decisiones_en_ruta = []

    for i in range(pasos + 1):
        lat = origen["lat"] + (lat_step * i)
        lng = origen["lng"] + (lng_step * i)

        decision = test_decision(lat, lng, velocidad_ms, use_osm=True)
        analisis = analizar_decision(decision)

        if "error" not in analisis:
            decisiones_en_ruta.append({
                "paso": i + 1,
                "posicion": {"lat": lat, "lng": lng},
                "accion": analisis["accion"],
                "riesgo": analisis["riesgo_score"],
            })

    print(f"\nPuntos en ruta: {len(decisiones_en_ruta)}")
    for d in decisiones_en_ruta:
        print(f"  Paso {d['paso']}: {d['accion']} (riesgo: {d['riesgo']:.2f})")


def main():
    """Función principal de pruebas."""
    print("=" * 70)
    print(" PRUEBAS COMPLETAS DE KRONOS - PUEBLA")
    print("=" * 70)

    # Verificar que el servicio esté disponible
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servicio no está disponible. Asegúrate de que Docker esté corriendo.")
            sys.exit(1)
        print("✓ Servicio disponible")
    except Exception as e:
        print(f"❌ Error al conectar con el servicio: {e}")
        print("   Asegúrate de que Docker esté corriendo: docker-compose up -d")
        sys.exit(1)

    resultados = []

    # 1. Pruebas de rutas completas
    print(f"\n{'='*70}")
    print("1. PRUEBAS DE RUTAS COMPLETAS")
    print(f"{'='*70}")

    for ruta in RUTAS_PRUEBA:
        resultado = test_ruta_completa(ruta)
        resultados.append(resultado)
        time.sleep(1)  # Pausa entre pruebas

    # 2. Pruebas de semáforos
    test_semaforos()

    # 3. Simulación de movimiento
    test_movimiento_simulado()

    # Resumen
    print(f"\n{'='*70}")
    print("RESUMEN DE PRUEBAS")
    print(f"{'='*70}")

    rutas_exitosas = sum(1 for r in resultados if "error" not in r.get("decision_ruta", {}))
    print(f"Rutas probadas: {len(resultados)}")
    print(f"Rutas exitosas: {rutas_exitosas}")
    print(f"Tasa de éxito: {rutas_exitosas/len(resultados)*100:.1f}%")

    # Guardar resultados
    with open("/tmp/kronos_test_results.json", "w") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Resultados guardados en /tmp/kronos_test_results.json")


if __name__ == "__main__":
    main()
