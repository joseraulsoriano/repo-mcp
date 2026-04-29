# Recetario Alexa + MCP

Repositorio con dos partes: el motor MCP (recetas, ingredientes, precios) y el backend para la skill Alexa.

- **recetario-mcp/** – Motor MCP en Python (FastAPI). Brave Search API + scraping supermercados. Expone `/mcp/recetario.*`.
- **backend-alexa/** – Backend Node.js para la skill Alexa. Expone `/api/mcp/recipes`, `/api/mcp/ingredients`, etc. y llama a recetario-mcp cuando `MCP_BASE_URL` esta definido.

Flujo: Alexa (Lambda) -> backend-alexa -> recetario-mcp -> Brave / scraping.

## Estructura

```
recetario-alexa-mcp/
  recetario-mcp/     # Python, puerto 8012
  backend-alexa/     # Node, puerto 3001
```

## Uso local

1. **recetario-mcp:** `cd recetario-mcp && docker compose up -d` (o `python -m app.main`). Poner `BRAVE_API_KEY` en `.env` (plantilla `recetario-mcp/.env.example`).
2. **backend-alexa:** `cd backend-alexa && cp .env.example .env`, editar, luego `export $(grep -v '^#' .env | xargs)` y `node server.js`, o en una linea: `MCP_BASE_URL=http://localhost:8012 node server.js`. Si el puerto 3001 esta ocupado, usar `PORT=3101`.
3. **Claves alineadas (produccion):** si `recetario-mcp` tiene `API_KEY`, define `MCP_API_KEY` en el backend con el **mismo** valor. Si quieres proteger el backend frente a Internet, define `API_KEY` en el backend (Lambda debe enviar esa cabecera).
4. Lambda de Alexa: `API_RECETARIO_URL` = URL publica del backend (sin path final especifico; las rutas son `/api/mcp/...`).

## Despliegue (Render u otro)

- Web Service 1: root `recetario-mcp`, runtime Python, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Web Service 2: root `backend-alexa`, runtime Node, start `node server.js`. Variables: `MCP_BASE_URL` = URL HTTPS del servicio 1; opcional `MCP_API_KEY` / `API_KEY` como arriba.

## Documentacion

- **recetario-mcp/README.md** – Tools, Brave API, Docker, API key.
- **backend-alexa/README.md** – Endpoints, MCP_BASE_URL, API key, pruebas.

No se sube `.env`; usar `.env.example` en cada carpeta como plantilla.
