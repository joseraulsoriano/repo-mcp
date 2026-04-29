# Persistencia de Datos - Kronos

Guía sobre el sistema de persistencia de perfiles de usuario y rutas en Kronos.

---

## Sistema de Persistencia

Kronos guarda información del usuario y sus rutas asociadas al `user_id`.

### Almacenamiento Actual

Por ahora, el sistema usa **archivos JSON** para persistencia simple:
- Ubicación: `/tmp/kronos_users.json`
- Formato: JSON con estructura de usuarios, rutas y destinos frecuentes

**Nota:** En producción, esto debería migrarse a una base de datos real (MongoDB, PostgreSQL).

---

## Datos Guardados por User ID

### 1. Perfil de Usuario

**Endpoint:** `POST /api/v1/user/setup`

Al configurar un perfil, se guarda:
- `user_id`: ID único generado automáticamente
- `name`: Nombre del usuario
- `home_location`: Ubicación de casa (lat, lng)
- `destination`: Destino actual (lat, lng)
- `destination_name`: Nombre del destino (ej: "Trabajo")
- `bike_specs`: Especificaciones de la moto
- `preferred_speed`: Velocidad preferida en m/s
- `risk_tolerance`: Tolerancia al riesgo

**Se guarda automáticamente** al llamar a `/api/v1/user/setup`.

---

### 2. Rutas Guardadas

**Endpoint:** `POST /api/v1/user/{user_id}/routes`

Guarda rutas específicas asociadas a un usuario:

```bash
curl -X POST "http://localhost:8000/api/v1/user/{user_id}/routes?origin_lat=19.0425&origin_lng=-98.1981&destination_lat=19.0500&destination_lng=-98.2267&route_name=Casa a Trabajo"
```

**Datos guardados:**
- `origin`: Posición de origen
- `destination`: Posición de destino
- `name`: Nombre de la ruta (opcional)

---

### 3. Destinos Frecuentes

**Endpoint:** `POST /api/v1/user/setup` (automático cuando se proporciona `destination_name`)

Se guardan automáticamente destinos frecuentes cuando tienen nombre:
- "Trabajo"
- "Casa"
- "Universidad"
- etc.

---

## Consultar Datos Guardados

### Obtener Perfil de Usuario

```bash
curl "http://localhost:8000/api/v1/user/{user_id}/profile"
```

**Respuesta:**
```json
{
    "user_id": "...",
    "name": "Usuario Prueba",
    "home_location": {"lat": 19.0425, "lng": -98.1981},
    "destination": {"lat": 19.0500, "lng": -98.2267},
    "bike_specs": {...},
    ...
}
```

---

### Obtener Rutas de Usuario

```bash
curl "http://localhost:8000/api/v1/user/{user_id}/routes"
```

**Respuesta:**
```json
{
    "user_id": "...",
    "routes": [
        {
            "origin": {"lat": 19.0425, "lng": -98.1981},
            "destination": {"lat": 19.0500, "lng": -98.2267},
            "name": "Casa a Trabajo"
        }
    ]
}
```

---

### Obtener Destinos Frecuentes

```bash
curl "http://localhost:8000/api/v1/user/{user_id}/destinations"
```

**Respuesta:**
```json
{
    "user_id": "...",
    "destinations": [
        {"name": "Trabajo", "lat": 19.0500, "lng": -98.2267},
        {"name": "Casa", "lat": 19.0425, "lng": -98.1981}
    ]
}
```

---

## Uso del Perfil en Decisiones

Al obtener una decisión, puedes usar el `user_id` para que el sistema use el perfil guardado:

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0425&lng=-98.1981&user_id={user_id}"
```

**El sistema automáticamente:**
- Usa `bike_specs.max_safe_accel` del perfil en lugar de valor por defecto
- Usa `preferred_speed` si no se proporciona velocidad
- Usa `risk_tolerance` del usuario
- Usa `bike_type` para evaluaciones específicas

---

## Flujo Completo

### 1. Configurar Perfil (se guarda automáticamente)

```bash
curl -X POST "http://localhost:8000/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan",
    "home_lat": 19.0425,
    "home_lng": -98.1981,
    "destination_lat": 19.0500,
    "destination_lng": -98.2267,
    "destination_name": "Trabajo",
    "bike_brand": "Honda",
    "bike_model": "CBR",
    "preferred_speed": 50
  }'
```

**Respuesta incluye `user_id`** que debes guardar para futuras consultas.

### 2. Usar Perfil en Decisiones

```bash
# Usar user_id para que el sistema use el perfil guardado
curl "http://localhost:8000/api/v1/decisions?lat=19.0425&lng=-98.1981&user_id={user_id}"
```

### 3. Guardar Ruta Específica

```bash
curl -X POST "http://localhost:8000/api/v1/user/{user_id}/routes?origin_lat=19.0425&origin_lng=-98.1981&destination_lat=19.0500&destination_lng=-98.2267&route_name=Ruta Diaria"
```

---

## Integración con MCP para Fichas Técnicas

### Visión Futura

El sistema está preparado para usar MCP (Model Context Protocol) para buscar fichas técnicas de motos en línea cuando no están en la base de datos local.

**Estructura preparada:**
- `BikeSpecsMCPService`: Servicio que busca en línea usando MCP
- Integración con web search para fichas técnicas
- Fallback a base de datos local si no se encuentra en línea

**Por ahora:**
- Usa base de datos local de motos comunes
- Crea especificaciones por defecto si no encuentra la moto

**Futuro con MCP:**
- Buscar en línea: "Honda CBR 600 ficha técnica especificaciones"
- Extraer datos: velocidad máxima, aceleración, etc.
- Guardar en cache para evitar búsquedas repetidas

---

## Archivo de Persistencia

### Ubicación

Por defecto: `/tmp/kronos_users.json`

### Estructura

```json
{
  "users": {
    "user-id-1": {
      "user_id": "user-id-1",
      "name": "Juan",
      "home_location": {"lat": 19.0425, "lng": -98.1981},
      "bike_specs": {...},
      ...
    }
  },
  "routes": {
    "user-id-1": [
      {
        "origin": {...},
        "destination": {...},
        "name": "Ruta 1"
      }
    ]
  },
  "frequent_destinations": {
    "user-id-1": [
      {"name": "Trabajo", "lat": 19.0500, "lng": -98.2267}
    ]
  }
}
```

---

## Migración a Base de Datos Real

### MongoDB (Recomendado)

Para migrar a MongoDB:

1. **Cambiar `UserStorage`** para usar `pymongo` en lugar de archivos JSON
2. **Colecciones:**
   - `users`: Perfiles de usuario
   - `routes`: Rutas asociadas a usuarios
   - `frequent_destinations`: Destinos frecuentes

### PostgreSQL (Alternativa)

Para PostgreSQL:
1. **Usar SQLAlchemy** para ORM
2. **Tablas:**
   - `users`: Perfiles de usuario
   - `routes`: Rutas (con foreign key a users)
   - `destinations`: Destinos frecuentes

---

## Ejemplos de Uso Completo

### Flujo Completo con Persistencia

```bash
# 1. Configurar perfil (se guarda automáticamente)
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan",
    "home_lat": 19.0425,
    "home_lng": -98.1981,
    "bike_brand": "Honda",
    "bike_model": "CBR"
  }')

# 2. Extraer user_id
USER_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['user_id'])")

# 3. Obtener decisión usando perfil guardado
curl "http://localhost:8000/api/v1/decisions?lat=19.0425&lng=-98.1981&user_id=$USER_ID"

# 4. Ver rutas guardadas
curl "http://localhost:8000/api/v1/user/$USER_ID/routes"
```

---

## Próximos Pasos

1. **MCP Integration**: Implementar búsqueda real usando MCP para fichas técnicas
2. **MongoDB Migration**: Migrar de JSON a MongoDB
3. **Cache de Fichas**: Cachear fichas técnicas encontradas vía MCP
4. **Historial de Rutas**: Guardar historial de rutas recorridas
5. **Estadísticas**: Analizar patrones de uso por usuario
