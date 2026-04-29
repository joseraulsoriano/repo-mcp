# Contratos del Motor (Input / Output)

Este documento define los contratos definitivos de entrada y salida del Policy Engine.

---

## Input — ContextSnapshot

Estructura completa del contexto que recibe el motor para evaluar decisiones.

```json
{
  "user": {
    "state": "ON_TIME | LATE | CRITICAL",
    "risk_tolerance": 0.3
  },
  "position": {
    "lat": 0.0,
    "lng": 0.0
  },
  "motion": {
    "speed": 0.0,
    "acceleration": 0.0
  },
  "bike": {
    "type": "urban",
    "max_safe_accel": 2.5
  },
  "route": {
    "distance_remaining": 300,
    "time_remaining": 25
  },
  "traffic": {
    "density": "FREE | SLOW | BLOCKED"
  },
  "signals": {
    "next_light": {
      "distance": 100,
      "state": "GREEN | YELLOW | RED",
      "remaining_time": 6
    },
    "following_light": {
      "distance": 200,
      "state": "GREEN"
    }
  },
  "confidence": 0.85
}
```

### Campos detallados

#### user
- `state`: Estado temporal del usuario respecto a su hora objetivo
- `risk_tolerance`: Tolerancia al riesgo (0.0 - 1.0)

#### position
- `lat`: Latitud actual
- `lng`: Longitud actual

#### motion
- `speed`: Velocidad actual en m/s
- `acceleration`: Aceleración actual en m/s²

#### bike
- `type`: Tipo de motocicleta (`urban | sport | work`)
- `max_safe_accel`: Aceleración máxima segura en m/s²

#### route
- `distance_remaining`: Distancia restante en metros
- `time_remaining`: Tiempo restante estimado en minutos

#### traffic
- `density`: Densidad de tráfico (`FREE | SLOW | BLOCKED`)

#### signals
- `next_light`: Información del próximo semáforo
  - `distance`: Distancia en metros
  - `state`: Estado actual
  - `remaining_time`: Tiempo restante en verde/rojo (segundos)
- `following_light`: Información del siguiente semáforo

#### confidence
- Nivel de confianza en los datos (0.0 - 1.0)

---

## Output — DecisionResult

Estructura de la decisión que devuelve el motor.

```json
{
  "decision": "PROCEED | WAIT | HOLD | FILTER_ALLOWED | FILTER_FORBIDDEN",
  "mode": "NORMAL | SAFE",
  "risk_score": 0.42,
  "message": "No filtres. No ganarás tiempo.",
  "confidence": 0.85
}
```

### Campos detallados

#### decision
Acción recomendada:
- `PROCEED`: Avanzar con normalidad
- `WAIT`: Esperar antes de avanzar
- `HOLD`: Mantener posición/velocidad actual
- `FILTER_ALLOWED`: Filtrar permitido (hay ganancia real)
- `FILTER_FORBIDDEN`: Filtrar prohibido (no hay ganancia o riesgo alto)

#### mode
Modo de operación:
- `NORMAL`: Evaluación estándar
- `SAFE`: Modo seguro (datos con baja confianza)

#### risk_score
Puntuación de riesgo de la acción (0.0 - 1.0)

#### message
Mensaje humano para el usuario. **Siempre debe ser claro y no inducir riesgo.**

#### confidence
Nivel de confianza en la decisión (0.0 - 1.0)

---

## Ejemplos de Uso

### Ejemplo 1: Semáforo alcanzable

**Input:**
```json
{
  "user": { "state": "ON_TIME", "risk_tolerance": 0.3 },
  "motion": { "speed": 15.0, "acceleration": 0.0 },
  "signals": {
    "next_light": {
      "distance": 50,
      "state": "GREEN",
      "remaining_time": 5
    }
  },
  "confidence": 0.9
}
```

**Output:**
```json
{
  "decision": "PROCEED",
  "mode": "NORMAL",
  "risk_score": 0.25,
  "message": "Puedes avanzar. El semáforo permanecerá en verde.",
  "confidence": 0.9
}
```

### Ejemplo 2: Filtrado no recomendado

**Input:**
```json
{
  "user": { "state": "LATE", "risk_tolerance": 0.4 },
  "traffic": { "density": "SLOW" },
  "route": { "distance_remaining": 200, "time_remaining": 10 },
  "confidence": 0.8
}
```

**Output:**
```json
{
  "decision": "FILTER_FORBIDDEN",
  "mode": "NORMAL",
  "risk_score": 0.65,
  "message": "No filtres. No ganarás tiempo y el riesgo aumenta.",
  "confidence": 0.8
}
```

### Ejemplo 3: Datos con baja confianza

**Input:**
```json
{
  "user": { "state": "ON_TIME", "risk_tolerance": 0.3 },
  "confidence": 0.45
}
```

**Output:**
```json
{
  "decision": "HOLD",
  "mode": "SAFE",
  "risk_score": 0.3,
  "message": "No puedo evaluar este tramo con precisión. Mantén carril y velocidad.",
  "confidence": 0.45
}
```
