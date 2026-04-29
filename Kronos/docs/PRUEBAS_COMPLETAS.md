# Pruebas Completas de Kronos - Puebla

Guía para ejecutar pruebas completas del sistema Kronos en Puebla.

---

## Script de Pruebas Completo

### Ejecutar Todas las Pruebas

```bash
python3 scripts/test_kronos_completo.py
```

---

## Qué Prueba el Script

### 1. Rutas Completas

Prueba movimiento entre lugares conocidos en Puebla:

- **Centro → Ángelopolis** (zona comercial)
- **Centro → Cholula** (ruta larga)
- **Centro → UDLAP** (zona universitaria)
- **Ángelopolis → Hospital** (zona sur)

**Para cada ruta verifica:**
- Distancia calculada
- Tiempo estimado
- Decisión en origen
- Decisión con destino (ruta completa)
- Decisión en destino
- Reducción de tiempo potencial (si se permite filtrar)

---

### 2. Detección de Semáforos

Prueba detección de semáforos usando OpenStreetMap:

- Centro Histórico
- Plaza Ángelopolis

**Verifica:**
- Si se detectan semáforos (confianza > 0.7)
- Mensajes relacionados con semáforos

---

### 3. Simulación de Movimiento

Simula movimiento paso a paso entre Centro y Ángelopolis:

- 5 puntos intermedios
- Decisiones en cada punto
- Análisis de riesgo en ruta

---

## Características Analizadas

### Decisiones del Policy Engine

- **Acción**: PROCEED, WAIT, HOLD, FILTER_ALLOWED, FILTER_FORBIDDEN
- **Modo**: NORMAL, SAFE
- **Riesgo**: Score (0.0-1.0) y nivel (LOW, MEDIUM, HIGH)
- **Confianza**: Nivel de confianza en los datos (0.0-1.0)

### Reducción de Tiempo

Si el sistema permite filtrar (`FILTER_ALLOWED`):
- Estima reducción de tiempo del 20%
- Compara tiempo normal vs tiempo con filtrado

### Semáforos

- Detecta semáforos cercanos usando OSM
- Considera estado del semáforo en decisiones
- Ajusta recomendaciones según semáforos

---

## Salida del Script

### Ejemplo de Salida

```
======================================================================
 RUTA: Centro → Ángelopolis (zona comercial)
======================================================================
Origen: Centro Histórico (Zócalo) (19.0425, -98.1981)
Destino: Plaza Ángelopolis (19.0500, -98.2267)
Distancia: 3.45 km (3450 m)
Velocidad: 50 km/h (13.89 m/s)
Tiempo estimado (normal): 4.1 minutos

📍 DECISIÓN EN ORIGEN:
  Acción: PROCEED
  Modo: NORMAL
  Riesgo: 0.15 (LOW)
  Mensaje: Tráfico fluido. Puedes avanzar normalmente.
  Confianza: 0.85

🛣️  DECISIÓN CON DESTINO (RUTA COMPLETA):
  Acción: FILTER_ALLOWED
  Modo: NORMAL
  Riesgo: 0.25 (LOW)
  Mensaje: Puedes filtrar. Ganarás tiempo.
  Confianza: 0.85

  ⏱️  REDUCCIÓN DE TIEMPO ESTIMADA:
     Tiempo normal: 4.1 min
     Tiempo con filtrado: 3.3 min
     Reducción: 0.8 min (19.5%)
```

---

## Resultados Guardados

Los resultados se guardan en JSON:

```bash
cat /tmp/kronos_test_results.json
```

**Estructura:**
```json
[
  {
    "ruta": "Centro → Ángelopolis (zona comercial)",
    "distancia_km": 3.45,
    "tiempo_estimado_min": 4.1,
    "decision_origen": {...},
    "decision_ruta": {...},
    "decision_destino": {...}
  }
]
```

---

## Verificar Funcionamiento

### 1. Servicio Disponible

```bash
curl "http://localhost:8000/health"
```

**Esperado:**
```json
{"status": "healthy"}
```

### 2. Decisión Básica

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0425&lng=-98.1981&speed=13.89&use_osm=true"
```

### 3. Decisión con Destino

```bash
curl -X POST "http://localhost:8000/api/v1/decisions" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0425,
    "lng": -98.1981,
    "speed": 13.89,
    "destination_lat": 19.0500,
    "destination_lng": -98.2267,
    "use_osm": true
  }'
```

---

## Lugares de Prueba en Puebla

| Lugar | Coordenadas | Descripción |
|-------|-------------|-------------|
| Centro | 19.0425, -98.1981 | Zócalo de Puebla |
| Ángelopolis | 19.0500, -98.2267 | Centro comercial |
| Cholula | 19.0631, -98.3033 | Centro de Cholula |
| UDLAP | 19.0408, -98.2231 | Universidad |
| Hospital Niño | 19.0589, -98.2300 | Hospital zona sur |
| Terminal CAPU | 19.0736, -98.2217 | Terminal autobuses |

---

## Métricas Esperadas

### Tasa de Éxito

- **Rutas probadas**: 4
- **Tasa de éxito esperada**: >90%

### Decisiones Válidas

- Decisiones deben tener `decision`, `mode`, `risk_score`
- `risk_score` entre 0.0 y 1.0
- `confidence` > 0.5 para ser válido

### Semáforos

- En Centro: Semáforos detectados (confianza > 0.7)
- En Ángelopolis: Semáforos detectados (confianza > 0.7)

---

## Troubleshooting

### Error: "El servicio no está disponible"

```bash
# Verificar que Docker esté corriendo
docker-compose ps

# Iniciar servicio
docker-compose up -d

# Ver logs
docker-compose logs --tail=30 kronos-api
```

### Error: "Timeout"

- Aumentar timeout en el script
- Verificar conexión a OpenStreetMap
- Revisar logs del servicio

### Decisiones con errores

- Verificar que `use_osm=true` esté configurado
- Revisar logs para errores de OSM
- Verificar coordenadas válidas

---

## Análisis de Resultados

### Comparar Rutas

Comparar tiempo estimado vs tiempo real con filtrado:

```python
# Ejemplo de análisis
for resultado in resultados:
    ruta = resultado["ruta"]
    tiempo_normal = resultado["tiempo_estimado_min"]
    decision = resultado["decision_ruta"]
    
    if decision["accion"] == "FILTER_ALLOWED":
        reduccion = tiempo_normal * 0.2
        print(f"{ruta}: {reduccion:.1f} min ahorrados")
```

### Verificar Semáforos

```python
# Contar detecciones de semáforos
semaforos_detectados = sum(
    1 for r in resultados
    if r["decision_origen"].get("confianza", 0) > 0.7
)
```

---

## Próximos Pasos

1. **Agregar más rutas**: Expandir lugares de prueba
2. **Métricas de rendimiento**: Medir tiempos de respuesta
3. **Pruebas de carga**: Probar con múltiples solicitudes simultáneas
4. **Validación de semáforos**: Verificar detección con datos reales
5. **Análisis de rutas óptimas**: Comparar con rutas sugeridas por Google Maps
