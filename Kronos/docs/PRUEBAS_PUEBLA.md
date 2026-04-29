# Pruebas con Ubicaciones Reales de Puebla

Esta guía explica cómo probar Kronos con ubicaciones geográficas reales de Puebla, México.

---

## Coordenadas de Puebla

### Ubicaciones de Prueba

- **Centro de Puebla**: `19.0414, -98.2063`
- **Ángelopolis**: `19.0500, -98.2267`
- **Cholula**: `19.0631, -98.3033`

---

## Uso del API

### Endpoint GET con Query Parameters

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=13.89"
```

**Parámetros:**
- `lat`: Latitud (requerido para usar ubicación específica)
- `lng`: Longitud (requerido para usar ubicación específica)
- `speed`: Velocidad en m/s (opcional, default: 10.0 m/s = 36 km/h)

**Ejemplo de respuesta:**
```json
{
    "decision": "PROCEED",
    "mode": "NORMAL",
    "risk_score": 0.15,
    "risk_level": "LOW",
    "message": "Tráfico fluido. Puedes avanzar normalmente.",
    "confidence": 0.85,
    "position": {
        "lat": 19.0414,
        "lng": -98.2063
    }
}
```

---

### Endpoint POST con Body JSON

```bash
curl -X POST http://localhost:8000/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0414,
    "lng": -98.2063,
    "speed": 13.89,
    "acceleration": 0.0
  }'
```

**Body JSON:**
```json
{
    "lat": 19.0414,
    "lng": -98.2063,
    "speed": 13.89,          // Opcional: m/s (50 km/h = 13.89 m/s)
    "acceleration": 0.0,     // Opcional: m/s²
    "destination_lat": 19.0500,  // Opcional: destino
    "destination_lng": -98.2267  // Opcional: destino
}
```

---

## Script de Prueba Automatizado

### Instalación de Dependencias

```bash
# Instalar requests (solo para el script de prueba)
pip install requests
```

### Ejecutar Pruebas

```bash
# Desde el directorio del proyecto
python scripts/test_puebla.py
```

El script prueba automáticamente:
1. Endpoint de salud (`/health`)
2. Tres ubicaciones de Puebla (Centro, Ángelopolis, Cholula)
3. Endpoints GET y POST para cada ubicación

---

## Conversión de Velocidades

Para facilitar el uso, aquí están algunas conversiones comunes:

| km/h | m/s | Descripción |
|------|-----|-------------|
| 30   | 8.33 | Zona escolar |
| 40   | 11.11 | Zona urbana |
| 50   | 13.89 | Avenidas principales |
| 60   | 16.67 | Periféricos |
| 70   | 19.44 | Carreteras |

---

## Ejemplos de Uso

### Centro de Puebla a velocidad urbana

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=11.11"
```

### Ángelopolis con destino

```bash
curl -X POST http://localhost:8000/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0500,
    "lng": -98.2267,
    "speed": 13.89,
    "destination_lat": 19.0414,
    "destination_lng": -98.2063
  }'
```

### Cholula con velocidad alta

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0631&lng=-98.3033&speed=16.67"
```

---

## Documentación Interactiva

Puedes probar directamente desde la documentación Swagger:

1. Abrir `http://localhost:8000/docs`
2. Ir a `/api/v1/decisions`
3. Hacer clic en "Try it out"
4. Ingresar coordenadas y parámetros
5. Ejecutar la petición

---

## Notas

- Si no proporcionas `lat` y `lng`, el sistema usa la configuración por defecto (mock)
- La velocidad se especifica en **metros por segundo** (m/s)
- La aceleración se especifica en **m/s²**
- Si proporcionas destino, el sistema calcula automáticamente la distancia usando la fórmula de Haversine

---

## Próximos Pasos

Para mejorar las pruebas con ubicaciones reales:

1. **Integrar OpenStreetMap/Nominatim**: Para obtener datos reales de calles y semáforos
2. **Integrar Google Maps API**: Para datos de tráfico en tiempo real
3. **Integrar Waze API**: Para datos de tráfico alternativos
4. **Agregar detección de POIs**: Para identificar semáforos cercanos en Puebla

---

## Ubicación Exacta

Si quieres probar con tu ubicación exacta:

1. Obtén tus coordenadas GPS desde tu teléfono o Google Maps
2. Úsalas en el endpoint:

```bash
curl "http://localhost:8000/api/v1/decisions?lat=TU_LAT&lng=TU_LNG&speed=13.89"
```

Reemplaza `TU_LAT` y `TU_LNG` con tus coordenadas exactas.
