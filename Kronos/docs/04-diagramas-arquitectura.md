# Diagramas de Arquitectura

Este documento contiene diagramas pseudo-UML claros, legibles en texto, alineados a Clean Architecture.

---

## 1. Diagrama de Contexto (Visión General)

```
┌────────────┐
│  Usuario   │
│ Motoclista │
└─────┬──────┘
      │ Contexto (ubicación, tiempo, moto)
      ▼
┌───────────────────────────┐
│   Sistema de Asistencia   │
│  (Policy Engine Backend)  │
└─────┬───────────┬─────────┘
      │           │
      ▼           ▼
┌──────────┐   ┌────────────┐
│  APIs    │   │ Sensores   │
│  Maps    │   │ GPS / IMU  │
└──────────┘   └────────────┘
```

**Nota:** El sistema no controla al usuario, recibe contexto y devuelve decisiones.

---

## 2. Diagrama de Capas (Clean Architecture)

```
┌────────────────────────────────────┐
│          Infraestructura            │
│ FastAPI | GPS | Traffic | Maps API  │
└────────────────────────────────────┘
                ▲
                │
┌────────────────────────────────────┐
│            Application              │
│ ContextAssembler                    │
│ RiskEvaluator                       │
│ PolicyEngine                        │
│ DecisionService                     │
└────────────────────────────────────┘
                ▲
                │
┌────────────────────────────────────┐
│              Dominio                │
│ ContextSnapshot                     │
│ RiskScore                           │
│ Policy                              │
│ Decision                            │
└────────────────────────────────────┘
```

**Regla de oro:** Nada del dominio sabe que existe FastAPI.

---

## 3. Diagrama de Clases (Dominio)

```
┌──────────────────────┐
│   ContextSnapshot    │
├──────────────────────┤
│ user_state           │
│ position             │
│ motion               │
│ bike                 │
│ route                │
│ traffic              │
│ signals              │
│ confidence           │
└──────────────────────┘

┌──────────────────────┐
│     RiskScore        │
├──────────────────────┤
│ value : float        │
│ level : LOW|MED|HIGH │
└──────────────────────┘

┌──────────────────────┐
│       Policy         │
├──────────────────────┤
│ name                 │
│ evaluate(context)    │
└──────────────────────┘

┌──────────────────────┐
│      Decision        │
├──────────────────────┤
│ action               │
│ message              │
│ mode                 │
│ risk_score           │
│ confidence           │
└──────────────────────┘
```

---

## 4. Diagrama de Secuencia (Flujo en Tiempo Real)

```
Usuario
  │
  │ Contexto (GPS, tiempo, moto)
  ▼
ContextAssembler
  │
  ▼
RiskEvaluator
  │
  │ calcula risk_score
  ▼
PolicyEngine
  │
  │ evalúa políticas
  ▼
DecisionService
  │
  ▼
Decision (respuesta)
```

**Flujo determinístico, sin magia.**

---

## 5. Diagrama del Policy Engine (Interno)

```
┌──────────────────────┐
│    PolicyEngine      │
├──────────────────────┤
│ evaluate(context)    │
└──────────┬───────────┘
           │
   ┌───────┴─────────┐
   │                 │
┌──────────┐   ┌──────────┐
│ Traffic  │   │ Signals  │
│ Policy   │   │ Policy   │
└──────────┘   └──────────┘
   │                 │
   └───────┬─────────┘
           ▼
     Risk Aggregation
           ▼
        Decision
```

---

## 6. Diagrama de Estados (Usuario)

```
        ┌──────────┐
        │ ON_TIME  │
        └────┬─────┘
             │ retraso
             ▼
        ┌──────────┐
        │  LATE    │
        └────┬─────┘
             │ crítico
             ▼
        ┌──────────┐
        │ CRITICAL │
        └──────────┘
```

**Nota:** El estado modifica reglas, no obliga acciones.

---

## 7. Diagrama de Decisiones (Simplificado)

```
             ┌───────────────┐
             │ ¿Datos fiables?│
             └───────┬───────┘
                     │ No
                     ▼
              SAFE MODE
                     │
                     ▼
           Mantener carril/velocidad
                     │
                     ▼
             ┌───────────────┐
             │ ¿Gana tiempo? │
             └───────┬───────┘
                     │ No
                     ▼
                 NO FILTRAR
```

---

## 8. Diagrama de Flujo de Datos

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────┐
│    FastAPI      │ (Transporte)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ ContextAssembler│
│  (recopila)     │
└──────┬──────────┘
       │ ContextSnapshot
       ▼
┌─────────────────┐
│  RiskEvaluator  │
└──────┬──────────┘
       │ RiskScore
       ▼
┌─────────────────┐
│  PolicyEngine   │
└──────┬──────────┘
       │ Decision
       ▼
┌─────────────────┐
│ DecisionService │
└──────┬──────────┘
       │ DecisionResult
       ▼
┌─────────────────┐
│    FastAPI      │ (Transporte)
└──────┬──────────┘
       │ HTTP Response
       ▼
┌─────────────┐
│   Usuario   │
└─────────────┘
```

---

## 9. Diagrama de Políticas (Jerarquía)

```
                Policy
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───────┐  ┌──────┐  ┌──────────┐
    │ Traffic│  │Signals│  │ Filtering│
    │ Policy │  │Policy │  │  Policy  │
    └───────┘  └──────┘  └──────────┘
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
              Decision
```

---

## Cómo Usar Estos Diagramas

Estos diagramas sirven para:
- **Implementar sin improvisar**
- **Explicar el sistema a terceros**
- **Escalar sin romper lógica**
- **Cambiar frameworks sin dolor**

**Esto es arquitectura viva, no documentación muerta.**
