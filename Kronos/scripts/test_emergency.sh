#!/bin/bash
# Script para probar funcionalidad de emergencias (911)

BASE_URL="http://localhost:8000"

echo "=================================================================="
echo "  Pruebas de Emergencias (911) - Kronos"
echo "=================================================================="

echo ""
echo "⚠️  IMPORTANTE: Este sistema NO llama al 911 real."
echo "   Solo registra emergencias y proporciona información útil."
echo "   El usuario DEBE llamar al 911 desde su teléfono."
echo ""

echo "1️⃣ Registrar emergencia - Accidente"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/emergency" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0425,
    "lng": -98.1981,
    "emergency_type": "accident",
    "description": "Accidente de tráfico en Centro"
  }' | python3 -m json.tool

echo ""
echo "2️⃣ Registrar emergencia - Médica"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/emergency" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0500,
    "lng": -98.2267,
    "emergency_type": "medical",
    "description": "Emergencia médica"
  }' | python3 -m json.tool

echo ""
echo "3️⃣ Registrar emergencia - Avería"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/emergency" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0631,
    "lng": -98.3033,
    "emergency_type": "breakdown",
    "description": "Moto descompuesta"
  }' | python3 -m json.tool

echo ""
echo "4️⃣ Estado del servicio de emergencias"
echo "------------------------------------------------------------------"
curl -s "${BASE_URL}/api/v1/emergency/status/health" | python3 -m json.tool

echo ""
echo "=================================================================="
echo "  Pruebas completadas"
echo "=================================================================="
