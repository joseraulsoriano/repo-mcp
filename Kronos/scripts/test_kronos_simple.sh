#!/bin/bash
# Script simple de pruebas de Kronos usando curl

BASE_URL="http://localhost:8000/api/v1"

echo "=================================================================="
echo "  PRUEBAS DE KRONOS - PUEBLA"
echo "=================================================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para probar decisión
test_decision() {
    local lat=$1
    local lng=$2
    local speed=$3
    local desc=$4
    
    echo ""
    echo "📍 $desc"
    echo "   Coordenadas: $lat, $lng"
    echo "   Velocidad: $speed m/s (~$(echo "$speed * 3.6" | bc | cut -d. -f1) km/h)"
    
    response=$(curl -s "${BASE_URL}/decisions?lat=${lat}&lng=${lng}&speed=${speed}&use_osm=true")
    
    decision=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('decision', 'ERROR'))" 2>/dev/null)
    risk=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('risk_score', 'N/A'))" 2>/dev/null)
    message=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('message', 'N/A'))" 2>/dev/null)
    
    if [ "$decision" != "ERROR" ]; then
        echo "   ✓ Decisión: $decision"
        echo "   ✓ Riesgo: $risk"
        echo "   ✓ Mensaje: $message"
    else
        echo "   ${RED}✗ Error al obtener decisión${NC}"
    fi
}

# Función para probar ruta con destino
test_route() {
    local origen_lat=$1
    local origen_lng=$2
    local destino_lat=$3
    local destino_lng=$4
    local speed=$5
    local desc=$6
    
    echo ""
    echo "🛣️  RUTA: $desc"
    echo "   Origen: $origen_lat, $origen_lng"
    echo "   Destino: $destino_lat, $destino_lng"
    
    response=$(curl -s -X POST "${BASE_URL}/decisions" \
      -H "Content-Type: application/json" \
      -d "{
        \"lat\": $origen_lat,
        \"lng\": $origen_lng,
        \"speed\": $speed,
        \"destination_lat\": $destino_lat,
        \"destination_lng\": $destino_lng,
        \"use_osm\": true
      }")
    
    decision=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('decision', 'ERROR'))" 2>/dev/null)
    risk=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('risk_score', 'N/A'))" 2>/dev/null)
    message=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('message', 'N/A'))" 2>/dev/null)
    
    if [ "$decision" != "ERROR" ]; then
        echo "   ✓ Decisión: $decision"
        echo "   ✓ Riesgo: $risk"
        echo "   ✓ Mensaje: $message"
        
        if [ "$decision" = "FILTER_ALLOWED" ]; then
            echo "   ${GREEN}⏱️  FILTRADO PERMITIDO: Se puede reducir tiempo${NC}"
        elif [ "$decision" = "FILTER_FORBIDDEN" ]; then
            echo "   ${YELLOW}⏱️  FILTRADO NO PERMITIDO: No se gana tiempo suficiente${NC}"
        fi
    else
        echo "   ${RED}✗ Error al obtener decisión${NC}"
    fi
}

# Verificar que el servicio esté disponible
echo "Verificando servicio..."
health=$(curl -s "http://localhost:8000/health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'ERROR'))" 2>/dev/null)

if [ "$health" != "healthy" ]; then
    echo "${RED}❌ Servicio no disponible. Ejecuta: docker-compose up -d${NC}"
    exit 1
fi

echo "${GREEN}✓ Servicio disponible${NC}"

# Pruebas de decisiones en lugares específicos
echo ""
echo "=================================================================="
echo "  1. PRUEBAS DE DECISIONES EN LUGARES ESPECÍFICOS"
echo "=================================================================="

test_decision 19.0425 -98.1981 13.89 "Centro Histórico (Zócalo)"
test_decision 19.0500 -98.2267 13.89 "Plaza Ángelopolis"
test_decision 19.0631 -98.3033 13.89 "Cholula Centro"

# Pruebas de rutas
echo ""
echo "=================================================================="
echo "  2. PRUEBAS DE RUTAS COMPLETAS"
echo "=================================================================="

test_route 19.0425 -98.1981 19.0500 -98.2267 13.89 "Centro → Ángelopolis"
test_route 19.0425 -98.1981 19.0631 -98.3033 13.89 "Centro → Cholula"
test_route 19.0425 -98.1981 19.0408 -98.2231 13.89 "Centro → UDLAP"

# Prueba de diferentes velocidades
echo ""
echo "=================================================================="
echo "  3. PRUEBAS CON DIFERENTES VELOCIDADES"
echo "=================================================================="

echo ""
echo "📍 Centro - Velocidad baja (30 km/h = 8.33 m/s):"
test_decision 19.0425 -98.1981 8.33 "Centro - Velocidad baja"

echo ""
echo "📍 Centro - Velocidad alta (80 km/h = 22.22 m/s):"
test_decision 19.0425 -98.1981 22.22 "Centro - Velocidad alta"

echo ""
echo "=================================================================="
echo "  PRUEBAS COMPLETADAS"
echo "=================================================================="
