#!/bin/bash
# Script para descargar y reproducir audio de bienvenida

BASE_URL="http://localhost:8000"
AUDIO_FILE="/tmp/kronos_welcome.mp3"

echo "Descargando audio de bienvenida..."
curl -s "${BASE_URL}/api/v1/welcome/audio" --output "${AUDIO_FILE}"

if [ -f "${AUDIO_FILE}" ]; then
    echo "✓ Audio descargado: ${AUDIO_FILE}"
    file "${AUDIO_FILE}"
    echo ""
    echo "Reproduciendo audio..."
    afplay "${AUDIO_FILE}"
    echo "✓ Audio reproducido"
else
    echo "✗ Error al descargar audio"
    exit 1
fi
