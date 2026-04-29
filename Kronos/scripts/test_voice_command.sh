#!/bin/bash
# Script para probar comandos de voz

BASE_URL="http://localhost:8000"

echo "=================================================================="
echo "  Prueba de Comandos de Voz - Kronos"
echo "=================================================================="

echo ""
echo "1️⃣ Probar comando: 'Kronos vamos a trabajo'"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kronos vamos a trabajo"}' | python3 -m json.tool

echo ""
echo "2️⃣ Probar comando: 'Kronos vamos a casa'"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kronos vamos a casa"}' | python3 -m json.tool

echo ""
echo "3️⃣ Probar comando: 'vamos a centro'"
echo "------------------------------------------------------------------"
curl -s -X POST "${BASE_URL}/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "vamos a centro"}' | python3 -m json.tool

echo ""
echo "4️⃣ Probar con GET (testing):"
echo "------------------------------------------------------------------"
curl -s "${BASE_URL}/api/v1/voice/command/test?text=Kronos vamos a trabajo" | python3 -m json.tool

echo ""
echo "=================================================================="
echo "  Pruebas completadas"
echo "=================================================================="
