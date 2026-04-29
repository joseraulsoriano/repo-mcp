# Sistema de Emergencias (911) - Kronos

Guía del sistema de emergencias integrado en Kronos.

---

## ⚠️ IMPORTANTE

**Este sistema NO llama al 911 real.**

El sistema de emergencias de Kronos:
- ✅ Registra emergencias y proporciona información útil
- ✅ Guía al usuario con pasos a seguir
- ✅ Guarda ubicación y detalles
- ❌ NO llama al 911 automáticamente
- ❌ NO contacta servicios de emergencia

**El usuario DEBE llamar al 911 desde su teléfono.**

---

## Funcionalidad

### Tipos de Emergencia Soportados

1. **Accidente** (`accident`)
   - Accidente de tráfico
   - Colisión
   - Incidente vial

2. **Médica** (`medical`)
   - Emergencia médica
   - Lesión
   - Problema de salud

3. **Avería** (`breakdown`)
   - Moto descompuesta
   - Problema mecánico
   - Necesita asistencia vial

4. **Otro** (`other`)
   - Cualquier otra emergencia

---

## Endpoints

### Registrar Emergencia

**POST** `/api/v1/emergency`

```bash
curl -X POST "http://localhost:8000/api/v1/emergency" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 19.0425,
    "lng": -98.1981,
    "emergency_type": "accident",
    "description": "Accidente en Centro",
    "user_id": "optional-user-id"
  }'
```

**Respuesta:**
```json
{
    "emergency_id": "uuid-generado",
    "status": "registered",
    "message": "Accidente registrado. Si puedes, sal del tráfico...",
    "location": {"lat": 19.0425, "lng": -98.1981},
    "timestamp": "2026-01-16T14:00:00",
    "next_steps": [
        "1. Sal del tráfico si puedes moverte",
        "2. Activa las luces de emergencia",
        "3. Llama al 911 desde tu teléfono",
        "4. No muevas a personas lesionadas",
        "5. Espera ayuda profesional"
    ]
}
```

### Consultar Emergencia

**GET** `/api/v1/emergency/{emergency_id}`

```bash
curl "http://localhost:8000/api/v1/emergency/{emergency_id}"
```

### Estado del Servicio

**GET** `/api/v1/emergency/status/health`

```bash
curl "http://localhost:8000/api/v1/emergency/status/health"
```

---

## Próximos Pasos por Tipo

### Accidente

1. Sal del tráfico si puedes moverte
2. Activa las luces de emergencia
3. **Llama al 911 desde tu teléfono**
4. No muevas a personas lesionadas
5. Espera ayuda profesional

### Emergencia Médica

1. Detente en un lugar seguro
2. **Llama al 911 desde tu teléfono**
3. Describe tu ubicación exacta
4. Sigue las instrucciones del operador
5. Mantén tu teléfono accesible

### Avería

1. Mueve la moto fuera del tráfico
2. Activa las luces de emergencia
3. Llama a asistencia vial
4. Espera en un lugar seguro
5. No intentes reparar en la carretera

---

## Integración en App Móvil

### Flujo Recomendado

1. **Usuario activa emergencia:**
   - Botón "Emergencia" en la app
   - O comando de voz: "Kronos emergencia"

2. **App registra emergencia:**
   - Envía POST a `/api/v1/emergency`
   - Recibe `emergency_id` y `next_steps`

3. **App muestra información:**
   - Próximos pasos en pantalla
   - Muestra mensaje: "Llama al 911 desde tu teléfono"
   - Botón para llamar al 911

4. **Usuario llama al 911:**
   - App puede abrir el marcador con 911
   - Usuario describe la situación
   - Usuario menciona que tiene ubicación registrada

---

## Monitoreo

### Métricas Registradas

- `emergencies.registered`: Total de emergencias registradas
- `emergencies.accident`: Emergencias de tipo accidente
- `emergencies.medical`: Emergencias médicas
- `emergencies.breakdown`: Averías

### Logs

Cada emergencia se registra en logs con:
- `emergency_id`
- Tipo de emergencia
- Ubicación (lat, lng)
- Timestamp
- User ID (si está disponible)

---

## Pruebas

### Script de Prueba

```bash
bash scripts/test_emergency.sh
```

**Prueba:**
- Registro de accidente
- Registro de emergencia médica
- Registro de avería
- Estado del servicio

---

## Limitaciones Actuales

1. **No llama al 911 real**: Requiere acción manual del usuario
2. **Sin notificaciones**: No notifica a contactos de emergencia
3. **Almacenamiento local**: Emergencias guardadas en memoria (no persistente)
4. **Sin tracking**: No rastrea el estado de la emergencia después del registro

---

## Futuras Mejoras

### Integración con Servicios Reales

1. **API de Emergencias** (si disponible):
   - Integración con sistemas de emergencia locales
   - Envío automático de ubicación

2. **Notificaciones:**
   - Notificar contactos de emergencia
   - SMS a familiares
   - Push notifications

3. **Persistencia:**
   - Guardar historial de emergencias
   - Analizar patrones

4. **Tracking:**
   - Actualizar estado de emergencia
   - Seguimiento en tiempo real

---

## Consideraciones de Seguridad

- ✅ **No llama automáticamente**: Evita falsas alarmas
- ✅ **Usuario debe confirmar**: Evita activaciones accidentales
- ✅ **Datos solo para guía**: No se comparte sin permiso
- ⚠️ **No reemplaza 911**: El usuario siempre debe llamar manualmente

---

## Uso en Producción

**Recomendaciones:**

1. **Mostrar advertencia clara:** "Este sistema NO llama al 911. Debes llamar manualmente."

2. **Facilitar llamada:** Botón directo para llamar al 911

3. **Guardar ubicación:** Mostrar coordenadas exactas para dar al operador

4. **Instrucciones claras:** Mostrar pasos a seguir según tipo de emergencia

5. **Logs importantes:** Registrar todas las emergencias para análisis posterior
