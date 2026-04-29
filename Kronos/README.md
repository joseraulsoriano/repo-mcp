# Kronos

Sistema de Asistencia para Motociclistas Urbanos

## Descripción

Kronos es un motor de decisión en tiempo real que reduce errores humanos mediante políticas de seguridad evaluables. Ayuda a los motociclistas a tomar decisiones correctas sin inducir maniobras riesgosas.

**Publicación / MCP:** Kronos es una **API de producto**, no un servidor MCP listo para catálogos de herramientas. Detalle: [docs/PUBLICACION_MCP.md](docs/PUBLICACION_MCP.md).

## Principio Fundamental

> **No estamos optimizando rutas, estamos reduciendo errores humanos en tiempo real.**

## Arquitectura

El proyecto sigue **Clean Architecture** con tres capas principales:

1. **Dominio** (`src/kronos/domain/`): Entidades y reglas de negocio puras (sin frameworks)
2. **Aplicación** (`src/kronos/application/`): Servicios que orquestan la lógica
3. **Infraestructura** (`src/kronos/infrastructure/`): FastAPI y proveedores externos

## Instalación

### Opción 1: Docker (Recomendado)

```bash
# Construir y levantar el servicio
docker-compose up --build

# O en modo detached
docker-compose up -d --build
```

La API estará disponible en `http://localhost:8000`

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -e .

# Instalar dependencias de desarrollo
pip install -e ".[dev]"
```

## Uso

### Ejecutar con Docker

```bash
# Levantar el servicio (producción)
docker-compose up

# Levantar el servicio (desarrollo con hot-reload)
docker-compose -f docker-compose.dev.yml up

# Ver logs
docker-compose logs -f

# Detener el servicio
docker-compose down
```

### Comandos Docker Útiles

```bash
# Reconstruir imagen
docker-compose build --no-cache

# Ejecutar en modo detached
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f kronos-api

# Ejecutar comandos dentro del contenedor
docker-compose exec kronos-api bash

# Detener y eliminar contenedores
docker-compose down -v

# Verificar importaciones (requiere pip install -e .)
make verify

# Probar API (requiere pip install -e ".[dev]")
make test-api
```

### Verificación del Servicio

Ver `docs/VERIFICACION.md` para una guía completa de verificación.

**Verificación rápida:**

```bash
# 1. Levantar el servicio
docker-compose up -d

# 2. Verificar health
curl http://localhost:8000/health

# 3. Verificar decisiones
curl http://localhost:8000/api/v1/decisions

# 4. Ver documentación
open http://localhost:8000/docs
```

### Ejecutar Localmente

```bash
uvicorn kronos.infrastructure.api:app --reload
```

La API estará disponible en `http://localhost:8000`

### Endpoints

- `GET /`: Información de la API
- `GET /health`: Estado de salud
- `GET /api/v1/decisions`: Obtener decisión actual (opcional: `?lat=X&lng=Y&speed=Z`)
- `POST /api/v1/decisions`: Generar nueva decisión (body JSON con coordenadas)

**Ejemplo con ubicación de Puebla:**
```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=13.89"
```

### Documentación

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Pruebas con Ubicaciones Reales

Kronos ahora soporta ubicaciones geográficas reales. Prueba con coordenadas de Puebla, México:

```bash
# Centro de Puebla
curl "http://localhost:8000/api/v1/decisions?lat=19.0414&lng=-98.2063&speed=13.89"

# Script automatizado de pruebas
python scripts/test_puebla.py
```

Ver `docs/PRUEBAS_PUEBLA.md` para más detalles sobre pruebas básicas.
Ver `docs/RUTAS_PUEBLA.md` para pruebas de rutas entre lugares conocidos.
Ver `docs/INTEGRACION_OSM.md` para usar OpenStreetMap con datos reales.
Ver `docs/SETUP_INICIAL.md` para el flujo de configuración inicial.
Ver `docs/VOZ.md` para comunicación por voz.
Ver `docs/PERSISTENCIA.md` para gestión de perfiles y rutas guardadas.

## Desarrollo

### Comandos Make (Recomendado)

```bash
# Ver ayuda
make help

# Construir imagen
make build

# Levantar servicio (producción)
make up

# Levantar servicio (desarrollo con hot-reload)
make dev

# Ver logs
make logs

# Detener servicio
make down

# Ejecutar tests
make test

# Formatear código
make format

# Linting
make lint
```

### Estructura del Proyecto

```
kronos/
├── docs/                    # Documentación de especificación
├── src/
│   └── kronos/
│       ├── domain/          # Entidades y políticas
│       ├── application/     # Servicios de aplicación
│       └── infrastructure/  # FastAPI y proveedores
├── pyproject.toml          # Configuración del proyecto
└── README.md
```

### Tests

```bash
pytest
```

### Linting

```bash
ruff check .
black --check .
mypy src/
```

### Formateo

```bash
black .
ruff check --fix .
```

## Documentación

La especificación completa del sistema está en `docs/`:

- `docs/01-politicas-policy-engine.md`: Políticas formales
- `docs/02-contratos-motor.md`: Contratos de entrada/salida
- `docs/03-arquitectura-backend.md`: Arquitectura del sistema
- `docs/04-diagramas-arquitectura.md`: Diagramas de diseño
- `docs/05-analisis-problema.md`: Análisis del problema

## Regla de Oro

> **Nada del dominio sabe que existe FastAPI.**

El dominio debe poder funcionar sin ninguna infraestructura externa.

## Licencia

[Por definir]

## Estado

**En desarrollo** - Versión 0.1.0
