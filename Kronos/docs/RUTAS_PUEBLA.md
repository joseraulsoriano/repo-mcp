# Pruebas de Rutas en Puebla

Guía para probar rutas entre lugares conocidos de Puebla usando Kronos.

---

## Lugares Disponibles

### Lugares Principales

| Clave | Nombre | Coordenadas | Descripción |
|-------|--------|-------------|-------------|
| `centro` | Centro Histórico (Zócalo) | 19.0425, -98.1981 | Plaza principal del centro histórico |
| `angelopolis` | Plaza Ángelopolis | 19.0500, -98.2267 | Centro comercial y zona residencial |
| `cholula` | Cholula Centro | 19.0631, -98.3033 | Centro de Cholula, cerca de la pirámide |
| `ufp` | Universidad UDLAP | 19.0408, -98.2231 | Universidad en San Andrés Cholula |
| `hospital` | Hospital del Niño | 19.0589, -98.2300 | Hospital principal zona sur |
| `terminal` | Terminal CAPU | 19.0736, -98.2217 | Terminal principal de autobuses |

---

## Scripts de Pruebas

### Opción 1: Script Simple (curl) - Recomendado

No requiere instalación adicional, solo curl:

```bash
# Ejecutar script simple
bash scripts/test_rutas_puebla_simple.sh
```

### Opción 2: Script Python Completo

Requiere instalación de requests:

```bash
# Instalar dependencias
pip install requests

# O usando pip3
pip3 install requests
```

### Uso Básico

#### Listar lugares disponibles

```bash
python scripts/test_rutas_puebla.py --list
```

#### Probar un lugar específico

```bash
# Probar Centro Histórico
python scripts/test_rutas_puebla.py --lugar centro --velocidad 50

# Probar Ángelopolis con velocidad de 60 km/h
python scripts/test_rutas_puebla.py --lugar angelopolis --velocidad 60
```

#### Probar una ruta entre dos lugares

```bash
# Ruta Centro → Ángelopolis
python scripts/test_rutas_puebla.py --origen centro --destino angelopolis --velocidad 50

# Ruta Centro → Cholula
python scripts/test_rutas_puebla.py --origen centro --destino cholula --velocidad 40

# Ruta Ángelopolis → Cholula
python scripts/test_rutas_puebla.py --origen angelopolis --destino cholula --velocidad 60
```

#### Probar todas las rutas principales

```bash
# Probar todas las rutas con velocidad de 50 km/h
python scripts/test_rutas_puebla.py --all-routes --velocidad 50

# Con velocidad de 60 km/h
python scripts/test_rutas_puebla.py --all-routes --velocidad 60
```

---

## Qué Muestra el Script

### Para Cada Ruta

1. **Información de la ruta**:
   - Distancia en km y metros
   - Velocidad configurada
   - Tiempo estimado de viaje

2. **Decisión en el origen**:
   - Decisión del Policy Engine
   - Riesgo calculado
   - Mensaje para el usuario

3. **Decisión en el destino**:
   - Decisión al llegar
   - Características detectadas

4. **Ruta completa**:
   - Decisión usando POST con destino
   - Toma en cuenta toda la ruta

### Para Ubicaciones Individuales

1. **Con OpenStreetMap** (`use_osm=true`):
   - Detecta semáforos reales de OSM
   - Datos de calles reales

2. **Sin OpenStreetMap** (`use_osm=false`):
   - Usa datos mock para comparación
   - Útil para debugging

---

## Ejemplos de Rutas Populares

### Ruta 1: Centro → Ángelopolis

**Distancia aproximada**: ~3.5 km
**Tiempo estimado** (a 50 km/h): ~4 minutos

```bash
python scripts/test_rutas_puebla.py --origen centro --destino angelopolis
```

**Características**:
- Cruza por zona comercial
- Varios semáforos en la ruta
- Tráfico variable según hora del día

---

### Ruta 2: Centro → Cholula

**Distancia aproximada**: ~10 km
**Tiempo estimado** (a 50 km/h): ~12 minutos

```bash
python scripts/test_rutas_puebla.py --origen centro --destino cholula
```

**Características**:
- Ruta más larga
- Sale del centro hacia periferia
- Más semáforos y cruces

---

### Ruta 3: Centro → UDLAP

**Distancia aproximada**: ~3 km
**Tiempo estimado** (a 50 km/h): ~3-4 minutos

```bash
python scripts/test_rutas_puebla.py --origen centro --destino ufp
```

**Características**:
- Ruta hacia zona universitaria
- Tráfico moderado
- Varios semáforos en Cholula

---

## Interpretación de Resultados

### Decisiones Comunes

- **`PROCEED`**: Puedes avanzar normalmente
- **`WAIT`**: Espera antes de avanzar (semáforo en rojo)
- **`HOLD`**: Mantén tu posición actual
- **`FILTER_ALLOWED`**: Filtrar permitido (ganancia de tiempo)
- **`FILTER_FORBIDDEN`**: No filtrar (sin ganancia o riesgo alto)

### Niveles de Riesgo

- **`LOW`** (< 0.33): Riesgo bajo
- **`MED`** (0.33 - 0.66): Riesgo medio
- **`HIGH`** (> 0.66): Riesgo alto

### Modos

- **`NORMAL`**: Evaluación estándar
- **`SAFE`**: Modo seguro (datos con baja confianza)

---

## Detección de Semáforos con OSM

Cuando usas `use_osm=true`, el sistema:

1. **Consulta Overpass API** para encontrar semáforos (`highway=traffic_signals`) en un radio de 500m
2. **Ordena por distancia** los semáforos encontrados
3. **Usa el más cercano** para la decisión
4. **Cachea resultados** por 5 minutos para evitar consultas repetidas

**Nota**: OSM no proporciona el estado en tiempo real de los semáforos (verde/amarillo/rojo). Por defecto se asume `GREEN`. En producción, esto debería venir de APIs de tráfico en tiempo real.

---

## Variables de Velocidad

El script permite especificar velocidad en km/h:

| km/h | m/s | Descripción |
|------|-----|-------------|
| 30   | 8.33 | Zona escolar, centro histórico |
| 40   | 11.11 | Zona urbana residencial |
| 50   | 13.89 | Avenidas principales (default) |
| 60   | 16.67 | Periféricos, zonas rápidas |
| 70   | 19.44 | Carreteras (no recomendado en ciudad) |

---

## Troubleshooting

### El servicio no responde

```bash
# Verificar que esté corriendo
docker-compose ps

# Ver logs
docker-compose logs kronos-api

# Reiniciar si es necesario
docker-compose restart
```

### Error en consulta OSM

- **Timeout**: Overpass API puede tardar. El script tiene timeout de 30 segundos.
- **Sin semáforos**: Si no encuentra semáforos, usa valores por defecto.
- **Cache**: Los resultados se cachean, espera 5 minutos para nueva consulta.

### Resultados inesperados

- Verifica las coordenadas de los lugares
- Revisa que `use_osm=true` esté activado si quieres datos reales
- Compara con `use_osm=false` para ver la diferencia

---

## Próximos Pasos

Para mejorar las pruebas:

1. **Agregar más lugares**: Edita `PUEBLA_LUGARES` en el script
2. **Integrar estado real de semáforos**: Usar Google Maps Traffic API
3. **Mejorar cálculo de rutas**: Usar OSRM o GraphHopper para rutas reales
4. **Agregar datos de tráfico**: Integrar APIs de tráfico en tiempo real
