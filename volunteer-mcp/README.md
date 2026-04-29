# Volunteer MCP

FastAPI MCP (Model Context Protocol) para búsqueda y ranking de voluntariados y educación, con enfoque México.

## Características

- **API HTTP con FastAPI** y CORS abierto
- **Búsqueda de voluntariados (MX)**: Worldpackers + resultados tipo noticias/listados (vía Brave)
- **Deduplicación y enlaces reales**: URL canónica y `apply_link` cuando exista
- **Datos educativos (MX)**: enriquecimiento de universidades y extracción de carreras/costos
- **MCP tools** expuestas vía endpoints `/mcp/*`
- **Prometheus metrics** en `/metrics`
- **Redis opcional** para caché y blobs; **SQLite/Postgres** para empleos

## Requisitos

- Python 3.11+
- Opcional: Redis (para caché y blobs)
- Opcional: Postgres (si usas `DATABASE_URL`), de lo contrario SQLite local
- Opcional: Brave Search API (`BRAVE_API_KEY`) para mejores resultados

## Configuración rápida (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Variables de entorno (opcional)
export BRAVE_API_KEY=tu_api_key   # mejora búsquedas
export REDIS_URL=redis://...      # cache/blobs
export DATABASE_URL=postgres://...# jobs storage; si no, SQLite local

# Iniciar servidor (desde la raíz del proyecto)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8011
```

### Con Docker (recomendado)

```bash
docker compose up --build
```

API en `http://127.0.0.1:8011`. El volumen `volunteer-data` persiste SQLite y JSON en `data/`. Variables opcionales: `BRAVE_API_KEY`, `REDIS_URL`, `DATABASE_URL` (en `.env` o en `environment` de `docker-compose.yml`).

## Arquitectura

Organización por capas y dominios:

```
volunteer-mcp/
├── app/
│   ├── main.py           # Punto de entrada FastAPI
│   ├── api/              # Rutas HTTP (health, metrics, /mcp/*, /education/*)
│   ├── mcp/               # Servidor MCP (herramientas voluntariados, jobs, educación)
│   ├── search/            # Búsqueda: Brave/DDG (provider), voluntariados, empleos
│   ├── storage/           # Persistencia: caché Redis, voluntariados, educación, jobs, learning
│   ├── ranking/           # Ranking de resultados (voluntariados)
│   └── metrics.py         # Prometheus
├── scripts/               # CLI datos educativos (enricher, details, combine)
├── data/                  # SQLite, JSON educativos (generados)
├── requirements.txt
├── Procfile
└── README.md
```

- **api**: endpoints REST y delegación al servidor MCP.
- **mcp**: lógica de cada herramienta MCP (volunteer.*, jobs.*, education.*, learning.*).
- **search**: proveedor Brave/DDG, agregadores voluntariados y empleos.
- **storage**: caché SWR, Redis, SQLite/Postgres para jobs y blobs educativos.

## Endpoints principales

### Salud/observabilidad
- `GET /health`
- `GET /metrics` (Prometheus)
- `GET /tools` (lista de herramientas MCP disponibles)

### MCP (POST JSON)
- `/mcp/volunteer.prompt_search`
- `/mcp/volunteer.search`
- `/mcp/volunteer.rank`
- `/mcp/volunteer.subscribe_alerts`
- `/mcp/volunteer.get_alerts`
- `/mcp/volunteer.collect`
- `/mcp/volunteer.mx_collect`
- `/mcp/volunteer.mx_search`
- `/mcp/volunteer.career_search`
- `/mcp/volunteer.area_search`
- `/mcp/education.search`
- `/mcp/jobs.search`
- `/mcp/jobs.list`
- `/mcp/learning.plan.save`
- `/mcp/learning.plan.get`

### Educación (GET)
- `GET /education/enriched` → lee `data/edu_enriched.json` o Redis `edu:enriched`
- `GET /education/details` → lee `data/edu_details.json` o Redis `edu:details`
- `GET /education/all` → une enriched + details on-the-fly
- `GET /education/skills?skills=...&match=any|all&state=...&tipo=...` → filtra por soft skills inferidas

## Utilidades CLI (datos educativos)

Ejecutar desde la raíz del proyecto (para que `app` esté en el path):

### Enriquecer con URLs (colegiaturas, carreras, currículo):
```bash
PYTHONPATH=. python scripts/education_enricher.py --in universidades_mx.json --out data/edu_enriched.json --max 100000
```

### Extraer detalles (carreras, costo):
```bash
python scripts/education_details.py --in data/edu_enriched.json --out data/edu_details.json --max 100000
```

### Combinar ambos en uno:
```bash
python scripts/education_combine.py --enriched data/edu_enriched.json --details data/edu_details.json --out data/edu_all.json
```

## Búsqueda de voluntariados (comportamiento)

- **Enfoque MX**: `collect_mexico` usa solo fuentes MX seguras:
  - Worldpackers (posiciones), con extracción de detalles + `apply_link`
  - Noticias/listados vía Brave (dominios gob.mx, Cruz Roja, TECHO, Worldpackers, voluntariado.net, UNV)
- **Deduplicación**: Por URL canónica y fusión de ítems duplicados (combina imágenes, conserva mejor score)
- **Enlaces "reales"**: Se prioriza `apply_link` cuando existe (acción), sin perder `link/source`

## Verificacion rapida (smoke)

Desde la raiz de `volunteer-mcp`, con el stack en marcha (`docker compose up -d`):

```bash
curl -s http://127.0.0.1:8011/health
curl -s http://127.0.0.1:8011/tools
curl -s -X POST http://127.0.0.1:8011/mcp/volunteer.search \
  -H "Content-Type: application/json" \
  -d '{"filters":{"location":"CDMX"}}'
curl -s -X POST http://127.0.0.1:8011/mcp/education.search \
  -H "Content-Type: application/json" \
  -d '{"query":"universidad","topK":2}'
```

El monorepo incluye CI que construye la imagen y comprueba `GET /health` y `GET /tools`: [.github/workflows/mcp-publish-smoke.yml](../.github/workflows/mcp-publish-smoke.yml).

## Ejemplos (curl)

### Voluntariados México (resultados normalizados)
```bash
curl -s -X POST http://127.0.0.1:8011/mcp/volunteer.mx_search \
  -H 'content-type: application/json' \
  -d '{"filters": {"location": "cdmx"}}' | jq '.count, .results[:2]'
```

### Educación: dataset combinado
```bash
curl -s http://127.0.0.1:8011/education/all | jq '.count, .data[:1]'
```

### Educación por soft skills
```bash
curl -s "http://127.0.0.1:8011/education/skills?skills=comunicacion,trabajo%20en%20equipo&match=all" | jq '.total'
```

### Jobs
```bash
curl -s -X POST http://127.0.0.1:8011/mcp/jobs.search \
  -H 'content-type: application/json' \
  -d '{"query":"data analyst mexico"}' | jq '.count, .saved_jobs'
```

## Variables de entorno

Plantilla: copia `.env.example` a `.env` y ajusta valores (no subas `.env` al repositorio).

- **BRAVE_API_KEY**: clave para Brave Search API (mejores resultados)
- **BRAVE_MAX_RPS**: límite de solicitudes por segundo (default `0.8`)
- **BRAVE_MONTHLY_QUOTA**: cuota mensual (default `2000`)
- **REDIS_URL**: URL de Redis (caché SWR y blobs `edu:*`, `vol:*`)
- **DATABASE_URL**: conexión a Postgres; si no se especifica, se usa `sqlite:///data/education_jobs.db`
- **DATA_DIR**: directorio de datos (por defecto `data`; en Docker suele ser `/app/data` vía volumen)

## Persistencia y métricas

- **Redis (opcional)**:
  - Caché SWR para búsquedas (`vol.search:*`, `vol.mx:*`, etc.)
  - Blobs educativos (`edu:enriched`, `edu:details`)
- **Base de datos (SQLite/Postgres)** para `jobs` vía SQLAlchemy
- **Prometheus** en `GET /metrics`

## Despliegue (Railway)

`Procfile`:
```bash
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Asegura configurar variables de entorno en Railway (especialmente `BRAVE_API_KEY` y `REDIS_URL` si aplica).

## Estructura principal (app/)

- `app/main.py`: punto de entrada FastAPI, CORS, router
- `app/api/routes.py`: endpoints HTTP (health, metrics, /mcp/*, /education/*)
- `app/mcp/server.py`: servidor MCP (herramientas volunteer.*, jobs.*, education.*, learning.*)
- `app/search/provider.py`: Brave/DDG, rate limits y cuotas
- `app/search/volunteer.py`: fuentes voluntariados, normalización MX, dedupe, `apply_link`
- `app/search/job.py`: búsqueda de empleos (Brave + dominios seguros)
- `app/ranking/volunteer.py`: ranking por score y filtros
- `app/storage/cache.py`: caché SWR (Redis o memoria)
- `app/storage/volunteer.py`, `education.py`, `learning.py`: persistencia
- `app/metrics.py`: Prometheus
- `scripts/`: CLI educación (education_enricher, education_details, education_combine)

## Notas

- **CORS:** en `app/main.py` está `allow_origins=["*"]`, práctico en desarrollo; en producción pública conviene restringir orígenes conocidos.
- La extracción de educación es heurística y dependiente del HTML; valida resultados
- Brave puede bloquearse si se exceden cuotas; revisa `BRAVE_MAX_RPS` y `BRAVE_MONTHLY_QUOTA`
- Para datos completos de educación, ejecuta los scripts CLI con `--max` alto antes de consumir los endpoints
