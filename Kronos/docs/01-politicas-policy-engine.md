# Policy Engine — Lógica Formal

Este documento define las políticas evaluables del sistema, sin ambigüedad.

---

## Política A — Semáforos

### Lenguaje humano
No intentes alcanzar un semáforo si no es seguro.

### Variables necesarias
- `distance_to_light`: Distancia al semáforo (metros)
- `current_speed`: Velocidad actual (m/s)
- `remaining_green_time`: Tiempo restante en verde (segundos)
- `required_acceleration`: Aceleración requerida para alcanzar (m/s²)
- `traffic_density`: Densidad de tráfico (`FREE | SLOW | BLOCKED`)

### Lógica formal

```
time_to_light = distance_to_light / current_speed

IF time_to_light <= remaining_green_time
AND required_acceleration <= MAX_SAFE_ACCEL
AND traffic_density != BLOCKED
THEN ALLOW_PROCEED
ELSE SUGGEST_WAIT
```

---

## Política B — Filtrado (Caso de 2 semáforos)

### Lenguaje humano
No filtres si no reduces tiempo real de llegada.

### Variables
- `distance_segment_1`: Distancia del segmento 1 (metros)
- `distance_segment_2`: Distancia del segmento 2 (metros)
- `light_1_state`: Estado semáforo 1 (`GREEN | YELLOW | RED`)
- `light_2_state`: Estado semáforo 2 (`GREEN | YELLOW | RED`)
- `traffic_segment_1`: Tráfico segmento 1
- `traffic_segment_2`: Tráfico segmento 2
- `avg_speed_no_filter`: Velocidad promedio sin filtrar (m/s)
- `avg_speed_filter`: Velocidad promedio filtrando (m/s)

### Evaluación de ganancia real

```
total_distance = distance_segment_1 + distance_segment_2
time_no_filter = total_distance / avg_speed_no_filter
time_filter = total_distance / avg_speed_filter
time_gain = time_no_filter - time_filter
```

### Política

```
IF time_gain > MIN_TIME_GAIN
AND risk_score < RISK_THRESHOLD
THEN ALLOW_FILTER
ELSE FORBID_FILTER
```

**Clave:** Filtrar no es acción base, solo se habilita si gana tiempo real, no "sensación".

---

## Política C — Estar Tarde

### Lenguaje humano
Estar tarde no justifica maniobras riesgosas.

### Lógica

```
IF user_state = LATE
THEN
  increase_risk_weight
  decrease_allowed_actions
  disable_filter_if_risk > LOW
```

### Mensaje adicional

```
IF repeated_late_behavior_detected
THEN notify_user_behavioral_warning
```

**(No castiga, educa)**

---

## Política D — Incertidumbre

### Lenguaje humano
Si no puedo decidir con confianza, conducen con precaución, no en silencio.

### Variables
- `data_confidence`: Nivel de confianza en los datos (0.0 - 1.0)
- `error_rate_estimate`: Estimación de tasa de error (0.0 - 1.0)

### Política

```
IF data_confidence < CONFIDENCE_MIN
OR error_rate_estimate > ERROR_MAX
THEN
  enforce_safe_mode
  issue_precaution_message
```

### Mensaje permitido
> "No puedo evaluar este tramo con precisión. Mantén carril y velocidad."

**Nunca deja al usuario sin guía.**

---

## Mensajes Prohibidos

El sistema **NUNCA** debe decir:
- "Corre"
- "Arriesga"
- "Pásate"
- "Intenta"
- "Acelera aunque no estés seguro"
- "Hazlo bajo tu responsabilidad"

**El lenguaje no puede inducir riesgo.**
