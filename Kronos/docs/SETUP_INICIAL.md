# Configuración Inicial de Kronos

Guía para el flujo de configuración inicial cuando el usuario inicia Kronos.

---

## Flujo de Configuración Inicial

Cuando un usuario inicia Kronos por primera vez, necesita configurar:

1. **Bienvenida** (voz neutral)
2. **Ubicación** (dónde vive/está ahora)
3. **Destino** (a dónde va)
4. **Moto** (tipo y modelo)
5. **Velocidad preferida**
6. **Tolerancia al riesgo** (opcional)

---

## Endpoints de Configuración

### 1. Bienvenida

#### Mensaje de Bienvenida (Texto)

```bash
curl "http://localhost:8000/api/v1/welcome/message"
```

**Respuesta:**
```json
{
    "message": "Bienvenido a Kronos. Tu asistente inteligente para motociclistas urbanos. Voy a ayudarte a llegar seguro a tu destino."
}
```

#### Audio de Bienvenida (Voz Neutral)

```bash
curl "http://localhost:8000/api/v1/welcome/audio" --output welcome.mp3
```

**Características:**
- Voz neutral (ni hombre ni niña)
- Acento español neutro (España)
- Formato MP3
- Duración: ~10 segundos

---

### 2. Instrucciones de Configuración

#### Audio de Instrucciones

```bash
curl "http://localhost:8000/api/v1/setup/audio" --output setup.mp3
```

**Mensaje:** "Antes de comenzar, necesito algunos datos. ¿Dónde estás ahora? ¿A dónde vas? ¿Qué tipo de motocicleta tienes?"

---

### 3. Consultar Ficha Técnica de Moto

#### Buscar Especificaciones (GET)

```bash
# Honda CBR 600
curl "http://localhost:8000/api/v1/bike/specs?brand=honda&model=cbr&engine_size=600"

# Italika FT 150
curl "http://localhost:8000/api/v1/bike/specs?brand=italika&model=ft&engine_size=150"

# Solo marca (encuentra la más común)
curl "http://localhost:8000/api/v1/bike/specs?brand=honda"
```

**Respuesta:**
```json
{
    "brand": "Honda",
    "model": "CBR 600",
    "year": null,
    "engine_size": 600.0,
    "max_speed": 280.0,
    "max_safe_accel": 4.5,
    "bike_type": "sport"
}
```

#### Buscar Especificaciones (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/bike/specs" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Honda",
    "model": "CBR",
    "engine_size": 600
  }'
```

---

### 4. Configurar Perfil Completo

#### Setup Completo (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
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
  }'
```

**Parámetros:**

- `name`: Nombre del usuario (opcional)
- `home_lat`, `home_lng`: Ubicación de casa/donde vive
- `destination_lat`, `destination_lng`: Destino del viaje
- `destination_name`: Nombre del destino (ej: "Trabajo", "Casa")
- `bike_brand`: Marca de la moto (requerido)
- `bike_model`: Modelo de la moto (opcional)
- `bike_engine_size`: Cilindraje en cc (opcional, ayuda a encontrar la ficha)
- `preferred_speed`: Velocidad preferida en km/h (opcional)
- `risk_tolerance`: Tolerancia al riesgo 0.0-1.0 (default: 0.3)

**Respuesta:**
```json
{
    "user_id": "uuid-generado",
    "name": "Juan Pérez",
    "home_location": {"lat": 19.0425, "lng": -98.1981},
    "destination": {"lat": 19.0500, "lng": -98.2267},
    "destination_name": "Trabajo",
    "bike_specs": {
        "brand": "Honda",
        "model": "CBR 600",
        "engine_size": 600.0,
        "max_safe_accel": 4.5,
        "bike_type": "sport"
    },
    "preferred_speed": 13.89,
    "risk_tolerance": 0.3
}
```

---

## Motos Soportadas

### Base de Datos Incluida

El sistema incluye fichas técnicas de motos comunes en México:

**Honda:**
- CBR 600 (sport)
- CB 500 (urban)
- CBF 150 (urban)

**Yamaha:**
- MT-07 (urban)
- R3 (sport)

**Kawasaki:**
- Ninja 300 (sport)

**Bajaj:**
- Pulsar 150 (urban)

**Italika:**
- FT 150 (urban)

**KTM:**
- Duke 200 (urban)

### Si la moto no está en la base de datos

El sistema crea especificaciones por defecto basadas en el cilindraje:
- **≥500cc**: Sport, max_safe_accel=4.0, max_speed=200 km/h
- **250-499cc**: Urban, max_safe_accel=3.0, max_speed=150 km/h
- **<250cc**: Urban, max_safe_accel=2.5, max_speed=120 km/h

---

## Voz Neutral

### Configuración

La bienvenida usa voz neutral con:
- **Idioma**: Español (`es`)
- **Acento**: Español de España (`tld="es"`) - más neutral que mexicano
- **Velocidad**: Normal

### Cómo Funciona

gTTS con acento español de España suena más neutral porque:
- Pronunciación más clara
- Menos marcado regionalmente
- Adecuado para instrucciones técnicas

---

## Flujo Completo Recomendado

### Paso 1: Bienvenida
```bash
# Reproducir audio de bienvenida
curl "http://localhost:8000/api/v1/welcome/audio" --output - | afplay -
```

### Paso 2: Instrucciones
```bash
# Reproducir instrucciones de configuración
curl "http://localhost:8000/api/v1/setup/audio" --output - | afplay -
```

### Paso 3: Consultar Moto
```bash
# Buscar especificaciones de la moto del usuario
curl "http://localhost:8000/api/v1/bike/specs?brand=honda&model=cbr"
```

### Paso 4: Configurar Perfil
```bash
# Configurar perfil completo
curl -X POST "http://localhost:8000/api/v1/user/setup" \
  -H "Content-Type: application/json" \
  -d '{ ... datos del usuario ... }'
```

---

## Script de Prueba Completo

```bash
# Ejecutar flujo completo de configuración
bash scripts/test_setup_inicial.sh
```

---

## Próximos Pasos

Una vez configurado el perfil:

1. **Usar perfil en decisiones**: Integrar `UserProfile` con `DecisionService`
2. **Persistencia**: Guardar perfil en base de datos
3. **Actualización**: Permitir actualizar perfil después de configuración inicial
4. **Múltiples destinos**: Guardar destinos frecuentes (Trabajo, Casa, etc.)

---

## Notas Técnicas

### Consulta Automática de Fichas

El sistema consulta automáticamente las fichas técnicas cuando el usuario proporciona:
- Marca de la moto
- Modelo (opcional)
- Cilindraje (opcional, ayuda a encontrar la correcta)

Si no encuentra la moto exacta, crea especificaciones por defecto basadas en el cilindraje.

### Integración con Decisiones

El perfil del usuario se puede usar en las decisiones para:
- Usar `bike_specs.max_safe_accel` en lugar de valor por defecto
- Usar `preferred_speed` si no se proporciona velocidad
- Usar `home_location` y `destination` para rutas frecuentes
