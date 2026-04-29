#!/bin/bash
# Script para probar el flujo de configuración inicial de Kronos

BASE_URL="http://localhost:8000"

echo "=================================================================="
echo "  Configuración Inicial de Kronos - Flujo Completo"
echo "=================================================================="

echo ""
echo "1️⃣ Bienvenida con voz neutral"
echo "------------------------------------------------------------------"
echo ""
echo "Mensaje de bienvenida:"
curl -s "${BASE_URL}/api/v1/welcome/message" | python3 -m json.tool

echo ""
echo "Audio de bienvenida (descargando...):"
curl -s "${BASE_URL}/api/v1/welcome/audio" --output /tmp/kronos_welcome.mp3
file /tmp/kronos_welcome.mp3
ls -lh /tmp/kronos_welcome.mp3

echo ""
echo "2️⃣ Audio de instrucciones de configuración"
echo "------------------------------------------------------------------"
echo ""
curl -s "${BASE_URL}/api/v1/setup/audio" --output /tmp/kronos_setup.mp3
file /tmp/kronos_setup.mp3

echo ""
echo "3️⃣ Consultar ficha técnica de moto"
echo "------------------------------------------------------------------"
echo ""
echo "Buscando Honda CBR 600:"
curl -s "${BASE_URL}/api/v1/bike/specs?brand=honda&model=cbr&engine_size=600" | python3 -m json.tool

echo ""
echo "Buscando Italika FT 150:"
curl -s "${BASE_URL}/api/v1/bike/specs?brand=italika&model=ft&engine_size=150" | python3 -m json.tool

echo ""
echo "4️⃣ Configurar perfil de usuario completo"
echo "------------------------------------------------------------------"
echo ""
curl -s -X POST "${BASE_URL}/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Usuario de Prueba",
    "home_lat": 19.0425,
    "home_lng": -98.1981,
    "destination_lat": 19.0500,
    "destination_lng": -98.2267,
    "destination_name": "Trabajo",
    "bike_brand": "Honda",
    "bike_model": "CBR",
    "bike_engine_size": 600,
    "preferred_speed": 50,
    "risk_tolerance": 0.3
  }' | python3 -m json.tool

echo ""
echo "=================================================================="
echo "  Configuración inicial completada"
echo "=================================================================="
