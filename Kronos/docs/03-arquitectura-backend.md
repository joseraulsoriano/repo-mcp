# Arquitectura Backend Limpia

Este documento define la arquitectura del sistema lista para implementar, siguiendo Clean Architecture.

---

## Visión General

Arquitectura en capas que separa dominio, aplicación e infraestructura.

---

## Capas de la Arquitectura

### Dominio (Core, sin frameworks)

Entidades y reglas de negocio puras. **No depende de nada externo.**

#### Entidades Principales

**ContextSnapshot**
- Representa el contexto completo del usuario, moto, ruta y entorno
- Contiene todos los datos necesarios para evaluar decisiones

**RiskScore**
- Calcula y representa el nivel de riesgo de una acción
- Valor numérico (0.0 - 1.0) y nivel categórico (`LOW | MED | HIGH`)

**Policy**
- Define una política evaluable
- Tiene nombre y método `evaluate(context: ContextSnapshot)`

**Decision**
- Representa el resultado de la evaluación de políticas
- Contiene acción, mensaje, modo, riesgo y confianza

---

### Application

Servicios de aplicación que orquestan la lógica de negocio.

#### Servicios Principales

**ContextAssembler**
- Recopila datos de múltiples fuentes (GPS, tráfico, mapas)
- Construye `ContextSnapshot` completo

**RiskEvaluator**
- Calcula `RiskScore` basado en contexto
- Considera factores: velocidad, tráfico, estado del usuario, confianza de datos

**PolicyEngine**
- Evalúa todas las políticas relevantes
- Agrega resultados y genera decisión final

**DecisionService**
- Orquesta: Context → Risk → Policy → Decision
- Genera respuesta final para el usuario

---

### Infrastructure

Capas externas, frameworks y servicios externos.

#### Componentes

**GPS Provider**
- Obtiene posición actual y velocidad
- Fuente: Sensores del dispositivo o API de GPS

**Traffic Provider**
- Obtiene datos de tráfico en tiempo real
- Fuente: APIs de tráfico (Google Maps, Waze, etc.)

**Map Provider**
- Obtiene información de ruta y semáforos
- Fuente: APIs de mapas (Google Maps, OpenStreetMap, etc.)

**FastAPI (Transporte)**
- Solo capa de transporte HTTP
- No contiene lógica de negocio

**Logger**
- Sistema de logging
- Fuente: Logging estándar o servicio externo

---

## Flujo Completo

```
Context → Risk Evaluation → Policy Engine → Decision → Response
```

### Flujo Detallado

1. **Usuario envía solicitud** (a través de FastAPI)
2. **ContextAssembler** recopila datos de proveedores
3. **ContextAssembler** construye `ContextSnapshot`
4. **RiskEvaluator** calcula `RiskScore`
5. **PolicyEngine** evalúa políticas relevantes
6. **PolicyEngine** genera decisión
7. **DecisionService** formatea respuesta
8. **FastAPI** devuelve `DecisionResult` al usuario

---

## Principios de Diseño

### Regla de Oro

**Nada del dominio sabe que existe FastAPI.**

El dominio debe poder funcionar sin ninguna infraestructura externa.

### Dependencias

```
Infrastructure → Application → Domain
```

- Infrastructure depende de Application
- Application depende de Domain
- Domain no depende de nada

### Inversión de Dependencias

Las interfaces se definen en Domain/Application.

Las implementaciones concretas están en Infrastructure.

---

## Módulos del Sistema

### Motor Central (Policy Engine)

**Responsabilidad única:** Tomar decisiones seguras en tiempo real.

**No guarda datos.**
**No muestra UI.**
**Solo decide.**

### Módulo de Ingesta

Recopila:
- Datos del usuario
- Datos de la moto
- Datos del entorno
- Datos históricos

### Módulo de Análisis

- Calcula rutas
- Evalúa riesgos
- Simula escenarios
- Descarta rutas inseguras

### Módulo de Decisión

- Filtrar o no
- Esperar o avanzar
- Acelerar o mantener

### Módulo de Comunicación

- Indicación clara
- Sin distracciones
- Visual + auditivo

### Módulo de Aprendizaje (Futuro)

- Aprende hábitos del usuario
- Ajusta tolerancia al riesgo
- Mejora predicción

---

## Tecnologías Recomendadas

### Stack Base

- **API**: FastAPI (Python)
- **Auth**: JWT
- **Logging**: Python logging + servicio externo
- **Deploy**: Docker

### Consideraciones de Datos

Este sistema es principalmente de decisión en tiempo real.

**No requiere base de datos persistente para el core del Policy Engine.**

Si se necesita historial:
- **Usuarios**: PostgreSQL (mínimo)
- **Datos flexibles**: MongoDB
- **Cache**: Redis

Pero el Policy Engine debe funcionar sin persistencia.

---

## Escalabilidad

### Diseño Stateless

El Policy Engine es stateless. Cada solicitud es independiente.

### Paralelización

Las evaluaciones pueden ejecutarse en paralelo sin conflictos.

### Horizontal Scaling

Múltiples instancias del Policy Engine pueden funcionar sin coordinación.

---

## Frase Clave

> **No estamos optimizando rutas, estamos reduciendo errores humanos en tiempo real.**
