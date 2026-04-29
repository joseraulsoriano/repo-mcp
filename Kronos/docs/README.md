# Especificación del Sistema de Asistencia para Motociclistas Urbanos

Este directorio contiene la especificación completa del sistema, organizada en documentos estructurados.

---

## Estructura de Documentos

### 1. Políticas del Policy Engine
**Archivo:** `01-politicas-policy-engine.md`

Define las políticas formales del sistema:
- Política A: Semáforos
- Política B: Filtrado (2 semáforos)
- Política C: Estar tarde
- Política D: Incertidumbre
- Mensajes prohibidos

---

### 2. Contratos del Motor
**Archivo:** `02-contratos-motor.md`

Define los contratos de entrada y salida:
- Input: `ContextSnapshot` (estructura completa)
- Output: `DecisionResult` (estructura completa)
- Ejemplos de uso

---

### 3. Arquitectura Backend Limpia
**Archivo:** `03-arquitectura-backend.md`

Define la arquitectura del sistema:
- Capas: Dominio, Aplicación, Infraestructura
- Flujo completo
- Principios de diseño
- Módulos del sistema
- Stack tecnológico

---

### 4. Diagramas de Arquitectura
**Archivo:** `04-diagramas-arquitectura.md`

Contiene diagramas pseudo-UML en texto:
- Diagrama de contexto
- Diagrama de capas
- Diagrama de clases (dominio)
- Diagrama de secuencia
- Diagrama del Policy Engine
- Diagrama de estados (usuario)
- Diagrama de decisiones
- Diagrama de flujo de datos
- Diagrama de políticas

---

### 5. Análisis del Problema
**Archivo:** `05-analisis-problema.md`

Análisis completo del problema:
- Problema en lenguaje humano
- Traducción a lógica
- Arquitectura inversa (módulos)
- Resumen de transformación

---

## Orden de Lectura Recomendado

1. **Análisis del Problema** (`05-analisis-problema.md`)
   - Entender el problema desde cero

2. **Políticas del Policy Engine** (`01-politicas-policy-engine.md`)
   - Entender las reglas del sistema

3. **Contratos del Motor** (`02-contratos-motor.md`)
   - Entender qué entra y qué sale

4. **Arquitectura Backend Limpia** (`03-arquitectura-backend.md`)
   - Entender la estructura del sistema

5. **Diagramas de Arquitectura** (`04-diagramas-arquitectura.md`)
   - Visualizar la arquitectura completa

---

## Conceptos Clave

### Policy Engine
Motor central que toma decisiones seguras en tiempo real. No guarda datos, no muestra UI, solo decide.

### Clean Architecture
Arquitectura en capas: Dominio (sin frameworks) → Aplicación (orquestación) → Infraestructura (frameworks).

### Principio Fundamental
> **No estamos optimizando rutas, estamos reduciendo errores humanos en tiempo real.**

### Regla de Oro
> **Nada del dominio sabe que existe FastAPI.**

---

## Estado de la Especificación

✅ **Completa y lista para implementación**

Esta especificación está completa y lista para comenzar la implementación del sistema.

No contiene código, pero define:
- Lógica formal
- Contratos claros
- Arquitectura limpia
- Diagramas de diseño

---

## Próximos Pasos

1. Revisar la especificación completa
2. Validar que responde al problema original
3. Comenzar implementación del dominio (sin frameworks)
4. Implementar aplicación y infraestructura
5. Tests y validación

---

## Notas

Esta especificación es **arquitectura viva, no documentación muerta**.

Debe evolucionar con el proyecto, pero manteniendo los principios fundamentales establecidos.
