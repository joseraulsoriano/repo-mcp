# Análisis del Problema (Humano → Lógico → Técnico)

Este documento contiene el análisis completo del problema desde lenguaje humano hasta arquitectura técnica, sin código.

---

## 1. Problema en Lenguaje Humano (Depurado)

### Problema Central

Los motociclistas urbanos sufren accidentes frecuentes porque toman decisiones riesgosas en tiempo real:

- Filtran entre autos sin necesidad
- Se saltan semáforos
- Calculan mal tiempos, distancias y aceleraciones
- Compensan retrasos con conducción agresiva

Esto pone en riesgo:
- Al propio motociclista
- A peatones
- A conductores

**La probabilidad de accidente aumenta cada vez que salen tarde.**

---

### Objetivo Humano

Ayudar al motociclista a:

- Llegar rápido, pero seguro
- Evitar maniobras inútiles (filtrar sin ganar tiempo)
- Tomar decisiones correctas en tiempo real
- Reducir accidentes sin exigirle pensar ni interactuar demasiado

---

### Qué debe decidir el usuario

- Si filtrar o no
- Si acelerar o mantener ritmo
- Si esperar o avanzar
- Si seguir una indicación o ignorarla

---

### Riesgo

Si el usuario no sigue las indicaciones, vuelve al estado base:

**Alta probabilidad de accidente**

---

## 2. Traducción a Lógica (Aquí nace el sistema)

Ahora quitamos emociones y dejamos reglas y entidades.

---

### Entidades (Cosas que existen)

#### Usuario
- Ubicación actual
- Destino
- Hora objetivo
- Historial de rutas
- Nivel de riesgo aceptable

#### Motocicleta
- Marca
- Cilindraje
- Aceleración
- Velocidad máxima segura
- Consumo
- Tipo (`urban | sport | work`)

#### Ruta
- Distancia
- Tiempo estimado
- Número de semáforos
- Puntos de detención
- Puntos de filtrado posibles
- Tramos peligrosos

#### Entorno (Tiempo real)
- Tráfico
- Semáforos
- Peatones
- Autos detenidos
- Flujo vehicular

---

### Estados

#### Usuario
- `ON_TIME`: A tiempo
- `LATE`: Tarde
- `CRITICAL`: Crítico

#### Ruta
- `SAFE`: Segura
- `FAST`: Rápida
- `RISKY`: Riesgosa
- `DISCARDED`: Descartada

---

### Reglas Clave (El corazón del algoritmo)

#### Regla 1 — Filtrado

```
Si filtrar NO reduce tiempo real
→ No filtrar
```

#### Regla 2 — Semáforo

```
Si probabilidad de alcanzar semáforo < X
→ No acelerar
```

#### Regla 3 — Retraso

```
Si usuario sale tarde
→ Ajustar ruta
→ NO inducir maniobras peligrosas
```

#### Regla 4 — Moto

```
Ruta válida SOLO si la moto puede recorrerla de forma segura
```

#### Regla 5 — Seguridad > Rapidez

```
Nunca sugerir acción que incremente riesgo por debajo de umbral
```

---

### Flujo Lógico

1. Usuario inicia trayecto
2. Sistema detecta contexto
3. Genera rutas posibles
4. Evalúa riesgo vs beneficio
5. Selecciona ruta óptima
6. Da indicaciones simples
7. Ajusta en tiempo real

---

## 3. Arquitectura Inversa (Qué módulos existen)

Aquí ya no hablamos de código, sino de bloques mentales.

---

### Motor Central (Policy Engine)

**Responsabilidad única:** Tomar decisiones seguras en tiempo real.

**No guarda datos.**
**No muestra UI.**
**Solo decide.**

---

### Módulo de Ingesta

Recopila:
- Datos del usuario
- Datos de la moto
- Datos del entorno
- Datos históricos

---

### Módulo de Análisis

- Calcula rutas
- Evalúa riesgos
- Simula escenarios
- Descarta rutas inseguras

---

### Módulo de Decisión

- Filtrar o no
- Esperar o avanzar
- Acelerar o mantener

---

### Módulo de Comunicación

- Indicación clara
- Sin distracciones
- Visual + auditivo

---

### Módulo de Aprendizaje (Futuro)

- Aprende hábitos del usuario
- Ajusta tolerancia al riesgo
- Mejora predicción

---

## 4. Paso Final: ¿Esto es Programación?

Sí.
Pero no empieza con código.

Empieza aquí:

```
Problema humano
→ reglas
→ decisiones
→ módulos
→ contratos
→ código
```

---

## Frase Clave para este Proyecto

> **No estamos optimizando rutas, estamos reduciendo errores humanos en tiempo real.**

---

## Resumen de la Transformación

### Nivel 1: Humano
- Problema: Motociclistas toman decisiones riesgosas
- Objetivo: Ayudar a decidir mejor en tiempo real

### Nivel 2: Lógico
- Entidades: Usuario, Moto, Ruta, Entorno
- Estados: ON_TIME, LATE, CRITICAL
- Reglas: Filtrado, Semáforo, Retraso, Moto, Seguridad

### Nivel 3: Técnico
- Dominio: ContextSnapshot, RiskScore, Policy, Decision
- Aplicación: ContextAssembler, RiskEvaluator, PolicyEngine, DecisionService
- Infraestructura: FastAPI, GPS Provider, Traffic Provider, Map Provider

---

## Validación de la Especificación

### ¿Responde al problema humano?
✅ Sí — Reduce decisiones riesgosas en tiempo real

### ¿Es evaluable sin ambigüedad?
✅ Sí — Políticas formales con lógica clara

### ¿Separa responsabilidades?
✅ Sí — Clean Architecture con capas bien definidas

### ¿Puede evolucionar sin romperse?
✅ Sí — Dominio independiente de infraestructura

### ¿Escala sin problemas?
✅ Sí — Stateless, paralelizable, horizontal scaling

---

## Próximos Pasos

1. Implementar dominio (sin frameworks)
2. Implementar aplicación (orquestación)
3. Implementar infraestructura (FastAPI, proveedores)
4. Tests unitarios del dominio
5. Tests de integración
6. Tests end-to-end

---

## Notas Finales

Esta especificación está lista para implementación.

**No es código, pero es programación.**

Es el mapa antes del viaje.
