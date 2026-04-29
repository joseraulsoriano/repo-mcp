# Integración con OpenStreetMap

Esta guía explica cómo usar OpenStreetMap (OSM) para obtener datos reales de calles, semáforos y rutas en Puebla.

---

## Características

### OpenStreetMap Integration

- **Detección de semáforos**: Encuentra semáforos reales cerca de tu ubicación
- **Cálculo de distancias**: Usa geopy para cálculos precisos
- **Búsqueda en radio**: Busca semáforos en un radio configurable (default: 500m)
- **Cache**: Evita consultas repetidas a Overpass API

---

## Uso del API con OSM

### Activar OSM en GET

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=13.89&use_osm=true"
```

**Parámetros:**
- `lat`: Latitud (requerido)
- `lng`: Longitud (requerido)
- `speed`: Velocidad en m/s (opcional)
- `use_osm`: Activar OSM (default: `false`)

---

### Activar OSM en POST

```bash
curl -X POST http://localhost:8000/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0414,
    "lng": -98.2063,
    "speed": 13.89,
    "use_osm": true
  }'
```

**Body JSON:**
```json
{
    "lat": 19.0414,
    "lng": -98.2063,
    "speed": 13.89,
    "use_osm": true,
    "destination_lat": 19.0500,
    "destination_lng": -98.2267
}
```

---

## Cómo Funciona

### OSMProvider

El `OSMProvider` usa Overpass API para consultar OpenStreetMap:

1. **Búsqueda de semáforos**: Consulta OSM para encontrar `highway=traffic_signals` cerca de tu ubicación
2. **Ordenamiento**: Ordena semáforos por distancia a tu ubicación
3. **Cache**: Guarda resultados en cache por 5 minutos para evitar consultas repetidas
4. **Cálculo de distancias**: Usa geopy para cálculos precisos de distancia

---

## Limitaciones

### Overpass API

- **Rate limiting**: Overpass API tiene límites de velocidad
- **Timeout**: Consultas pueden tardar hasta 10 segundos
- **Datos**: Depende de que OSM tenga datos actualizados de Puebla

### Estado de Semáforos

- OSM **no** proporciona el estado en tiempo real de semáforos (verde/amarillo/rojo)
- Por defecto, se asume `GREEN` (verde)
- En producción, esto debería venir de:
  - APIs de tráfico (Google Maps, Waze)
  - Sensores en tiempo real
  - Cámaras de tráfico

---

## Mejoras Futuras

### Datos en Tiempo Real

1. **Google Maps Traffic API**: Para estado real de semáforos
2. **Waze API**: Para datos de tráfico alternativos
3. **Sensores IoT**: Para datos locales de Puebla

### Routing Real

1. **OSRM**: Para cálculo de rutas reales usando OSM
2. **GraphHopper**: Alternativa a OSRM
3. **Google Directions API**: Para rutas optimizadas

---

## Ejemplos de Uso

### Centro de Puebla con OSM

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=13.89&use_osm=true"
```

### Ángelopolis a Centro con OSM

```bash
curl -X POST http://localhost:8000/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0500,
    "lng": -98.2267,
    "speed": 13.89,
    "destination_lat": 19.0414,
    "destination_lng": -98.2063,
    "use_osm": true
  }'
```

---

## Configuración

### Cache

El cache de OSM tiene un TTL de 5 minutos. Para modificar:

```python
# En src/kronos/infrastructure/providers/osm_provider.py
self._cache_ttl = 300  # Cambiar a tus necesidades
```

### Radio de Búsqueda

El radio de búsqueda por defecto es 500 metros. Para cambiar:

```python
# En src/kronos/infrastructure/providers/osm_provider.py
SEARCH_RADIUS = 500  # Cambiar a tus necesidades
```

---

## Debugging

### Ver consultas Overpass

Si necesitas ver qué consultas se hacen a Overpass:

```python
# En src/kronos/infrastructure/providers/osm_provider.py
print(f"Query: {query}")  # Agregar antes de ejecutar query
```

### Ver semáforos encontrados

```python
traffic_lights = osm_provider.find_traffic_lights(position)
print(f"Semáforos encontrados: {len(traffic_lights)}")
for tl in traffic_lights:
    print(f"  - ID: {tl['id']}, Distancia: {tl['distance']:.0f}m")
```

---

## Referencias

- [OpenStreetMap](https://www.openstreetmap.org/)
- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [Overpy Documentation](https://python-overpy.readthedocs.io/)
- [Geopy Documentation](https://geopy.readthedocs.io/)
