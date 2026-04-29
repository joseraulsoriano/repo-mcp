# Recetario MCP

Motor MCP para recetas, ingredientes, precios y supermercados (MX). Estilo volunteer-mcp: Brave Search API + scraping a paginas de supermercados (Walmart, Soriana, Chedraui) sin APIs de tienda.

## Flujo

Usuario habla con Alexa -> Alexa (Lambda) llama a backend-alexa -> backend-alexa llama a **recetario-mcp** (este servicio) -> tools usan Brave Search y scraping -> resultados a Alexa.

## Tools y rutas POST

| Tool | Ruta POST | Uso |
|------|-----------|-----|
| recetario.recipes_search | `/mcp/recetario.recipes_search` | Busqueda de recetas MX (Brave + dominios). |
| recetario.ingredients_search | `/mcp/recetario.ingredients_search` | Busqueda de ingredientes (Brave). |
| recetario.prices_search | `/mcp/recetario.prices_search` | Precios: Brave + scraping Walmart/Soriana/Chedraui (sin APIs de tienda). |
| recetario.stores_search | `/mcp/recetario.stores_search` | Supermercados / tiendas (Brave + dominios MX). |

## Requisitos

- Python 3.10+
- `BRAVE_API_KEY` (Brave Search API) para busquedas. Sin clave, las tools devuelven listas vacias.

## Instalacion y ejecucion

**Con Docker (recomendado, mas rapido):**

```bash
cd recetario-mcp
# Opcional: crear .env con BRAVE_API_KEY=tu_clave
docker compose up --build
```

Servicio en **http://127.0.0.1:8012**. Deja ese terminal con el contenedor en marcha y en **otra terminal** ejecuta los `curl`; si cierras con Ctrl+C el contenedor se detiene y curl devolvera "Connection refused" (exit 7).

**Alternativa: contenedor en segundo plano**

```bash
docker compose up -d --build
# Probar:
curl -s http://127.0.0.1:8012/health
# Detener cuando acabes:
docker compose down
```

Las variables de entorno se leen de `.env` o se pasan en `docker-compose.yml`.

**Proteccion (API key):** Si defines **API_KEY** en el MCP, las rutas `/mcp/*` y `/tools` requieren cabecera **X-API-Key** o **Authorization: Bearer &lt;key&gt;** con ese valor. `/health` queda libre. El backend-alexa debe enviar la misma clave (variable **MCP_API_KEY**) al llamar al MCP. Sin API_KEY el MCP sigue abierto (solo para desarrollo).

**Con entorno virtual:**

```bash
cd recetario-mcp
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env y poner BRAVE_API_KEY
python -m app.main
```

Por defecto corre en **http://127.0.0.1:8012**.

- **GET** `/health` -> estado del servicio.
- **GET** `/tools` -> lista de tools.
- **POST** `/mcp/recetario.recipes_search` body `{"query": "chilaquiles", "tipo_comida": "desayuno"}`.
- **POST** `/mcp/recetario.ingredients_search` body `{"query": "jitomate cebolla"}`.
- **POST** `/mcp/recetario.prices_search` body `{"query": "arroz", "scraping": true}`.
- **POST** `/mcp/recetario.stores_search` body `{"query": "supermercados", "location": "CDMX"}`.

## Brave Search API (implementacion oficial)

El MCP usa la **Web Search API** de Brave segun la documentacion oficial:

- **Documentacion general:** [Brave Search API - Documentation](https://api-dashboard.search.brave.com/documentation)
- **Web Search (GET):** [API Reference - Web search - Search GET](https://api-dashboard.search.brave.com/api-reference/web/search/get)
- **Servicio Web Search:** [Web search - Brave Search API](https://api-dashboard.search.brave.com/documentation/services/web-search)

Implementacion en `app/search/provider.py`:

- **Endpoint:** `GET https://api.search.brave.com/res/v1/web/search`
- **Autenticacion:** header `X-Subscription-Token` con la API key
- **Parametros usados:** `q` (obligatorio), `count` (max 20), `country`, `search_lang`, `extra_snippets`
- **Recetas/ingredientes MX:** todas las tools envian `country=MX` y `search_lang=es`; recipes e ingredients usan ademas `extra_snippets=true` para hasta 5 fragmentos extra por resultado (doc: [Extra Snippets](https://api-dashboard.search.brave.com/documentation/services/web-search)).
- **Paginacion:** la API admite `offset` (max 9); el provider expone `offset` en `search()` para uso futuro.
- **Rate limit y cuota:** respetamos RPS (`BRAVE_MAX_RPS`) y cuota mensual (`BRAVE_MONTHLY_QUOTA`); opcional Redis para cuota distribuida.

## Variables de entorno

| Variable | Uso |
|----------|-----|
| BRAVE_API_KEY | Clave Brave Search API (obligatoria para busquedas). |
| BRAVE_MAX_RPS | Rate limit (default 0.8). |
| BRAVE_MONTHLY_QUOTA | Cuota mensual (default 2000). |
| REDIS_URL | Opcional: cuota distribuida (instalar redis en requirements). |

## Scraping supermercados

Las precios se obtienen por **scraping** a paginas de Walmart, Soriana y Chedraui (sin APIs de tienda). Los selectores estan en `app/scraping/supermarkets.py`; si las paginas cambian, hay que actualizar los selectores.

## Estructura

```
recetario-mcp/
  app/
    main.py           # FastAPI
    api/routes.py     # POST /mcp/recetario.*
    mcp/server.py     # RecetarioMCPServer (tools)
    search/
      provider.py     # Brave Search API + rate limit y cuota
      recipes.py      # recetario.recipes_search
      ingredients.py  # recetario.ingredients_search
      prices.py       # recetario.prices_search (Brave + scraping)
      stores.py       # recetario.stores_search
    scraping/
      supermarkets.py  # fetch HTML + parse precio/nombre (Walmart, Soriana, Chedraui)
```

## Integracion con backend-alexa y Alexa

- **backend-alexa** puede hacer proxy a recetario-mcp: configurar `MCP_BASE_URL` apuntando a la URL de recetario-mcp (ej. `https://recetario-mcp.railway.app`) y reenviar las peticiones a `/mcp/recetario.*`.
- La skill Alexa (Lambda) llama a backend-alexa; backend-alexa llama a recetario-mcp y devuelve la respuesta a Alexa.
