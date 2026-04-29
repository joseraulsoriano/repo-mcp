#!/bin/bash
# Script simple para probar rutas en Puebla usando curl

BASE_URL="http://localhost:8000"

echo "=================================================================="
echo "  Pruebas de Rutas en Puebla - Kronos"
echo "=================================================================="

echo ""
echo "Lugares disponibles:"
echo "  centro     - Centro Histórico (Zócalo): 19.0425, -98.1981"
echo "  angelopolis - Plaza Ángelopolis: 19.0500, -98.2267"
echo "  cholula    - Cholula Centro: 19.0631, -98.3033"
echo "  ufp        - Universidad UDLAP: 19.0408, -98.2231"
echo ""

echo "------------------------------------------------------------------"
echo "  Ruta: Centro → Ángelopolis"
echo "------------------------------------------------------------------"
echo ""
echo "📏 Distancia: ~3.5 km"
echo "⏱️  Tiempo estimado (50 km/h): ~4 minutos"
echo ""

echo "🔵 Origen: Centro Histórico"
curl -s "${BASE_URL}/api/v1/decisions?lat=19.0425&lng=-98.1981&speed=13.89&use_osm=true" | python3 -m json.tool

echo ""
echo "🔴 Destino: Plaza Ángelopolis"
curl -s "${BASE_URL}/api/v1/decisions?lat=19.0500&lng=-98.2267&speed=13.89&use_osm=true" | python3 -m json.tool

echo ""
echo "🔄 Ruta completa (POST con destino):"
curl -s -X POST "${BASE_URL}/api/v1/decisions" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0425,
    "lng": -98.1981,
    "speed": 13.89,
    "destination_lat": 19.0500,
    "destination_lng": -98.2267,
    "use_osm": true
  }' | python3 -m json.tool

echo ""
echo "------------------------------------------------------------------"
echo "  Ruta: Centro → Cholula"
echo "------------------------------------------------------------------"
echo ""
echo "📏 Distancia: ~10 km"
echo "⏱️  Tiempo estimado (50 km/h): ~12 minutos"
echo ""

echo "🔵 Origen: Centro Histórico"
curl -s "${BASE_URL}/api/v1/decisions?lat=19.0425&lng=-98.1981&speed=13.89&use_osm=true" | python3 -m json.tool

echo ""
echo "🔴 Destino: Cholula Centro"
curl -s "${BASE_URL}/api/v1/decisions?lat=19.0631&lng=-98.3033&speed=13.89&use_osm=true" | python3 -m json.tool

echo ""
echo "🔄 Ruta completa (POST con destino):"
curl -s -X POST "${BASE_URL}/api/v1/decisions" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0425,
    "lng": -98.1981,
    "speed": 13.89,
    "destination_lat": 19.0631,
    "destination_lng": -98.3033,
    "use_osm": true
  }' | python3 -m json.tool

echo ""
echo "=================================================================="
echo "  Pruebas completadas"
echo "=================================================================="
