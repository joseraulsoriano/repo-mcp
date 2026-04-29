# Backend Alexa - Recetario MX

Backend Node.js modular para la skill Alexa Recetario MX. Sin dependencias externas. Misma interfaz que el MCP de recetario-mx (`/api/mcp/*`). Se alimenta del **motor MCP** (recetas, ingredientes, precios, supermercados); ese motor puede estar en recetario-mx o en un servicio aparte. Ver **MCP_MOTOR.md** para donde implementar el motor y como conectar este backend con el MCP real (opcional proxy).

## Arquitectura

Estructura por secciones (recetas, ingredientes, sugerencias/menu, precios/compras), no monolito:

```
backend-alexa/
  server.js           # Entrada: enrutador y CORS
  lib/
    response.js       # Respuesta JSON + CORS
    parseBody.js      # Parseo de body POST
  routes/             # Una ruta por seccion MCP
    recipes.js        # POST /api/mcp/recipes
    ingredients.js    # GET/POST /api/mcp/ingredients
    suggestions.js    # POST /api/mcp/suggestions
    prices.js         # GET /api/mcp/prices
    health.js         # GET /health
  data/               # Datos demo por dominio
    recipes.js        # Recetas por tipoComida
    ingredients.js    # Lista ingredientes
    suggestions.js    # Menu (desayuno, comida, cena)
    prices.js         # Precios por ingrediente
```

| Seccion        | Endpoint                  | Metodo | Uso en Alexa / MCP                    |
|----------------|---------------------------|--------|---------------------------------------|
| Recetas        | `/api/mcp/recipes`        | POST   | Ver recetas por tipo de comida        |
| Ingredientes  | `/api/mcp/ingredients`    | GET    | Listar ingredientes (?userId=)        |
| Ingredientes  | `/api/mcp/ingredients`    | POST   | Anadir ingrediente (demo, no persiste) |
| Sugerencias   | `/api/mcp/suggestions`    | POST   | Menu del dia (tiposComida, presupuesto) |
| Precios/Compras | `/api/mcp/prices`       | GET    | Precios de ingredientes (?userId=)    |
| Salud         | `/health`                 | GET    | Estado del servicio                   |

## Conexion con recetario-mcp (busqueda real)

Si defines **MCP_BASE_URL**, el backend llama a recetario-mcp en lugar de usar datos demo:

- **Recetas:** POST `/api/mcp/recipes` -> `recetario.recipes_search` (query + tipo_comida)
- **Ingredientes:** GET `/api/mcp/ingredients` -> `recetario.ingredients_search` (?q= opcional)
- **Sugerencias:** POST `/api/mcp/suggestions` -> varias llamadas a `recipes_search` (desayuno, comida, cena)
- **Precios:** GET `/api/mcp/prices` -> `recetario.prices_search` (?q= opcional)

**Local:** levanta recetario-mcp (ej. `docker compose up -d` en `recetario-mcp`) y luego:

```bash
cd backend-alexa
export MCP_BASE_URL=http://localhost:8012
# o: cp .env.example .env && editar .env; luego: export $(grep -v '^#' .env | xargs)
node server.js
```

Si MCP_BASE_URL no esta definido, se usan los datos demo (data/*).

## Proteccion (API key)

Si defines **API_KEY** en el backend, las rutas `/api/mcp/*` requieren cabecera **X-API-Key** o **Authorization: Bearer &lt;key&gt;** con ese valor. `/health` y OPTIONS siguen abiertos.

- **Lambda (Alexa):** Pon la misma clave en variable de entorno del Lambda (ej. `API_RECETARIO_KEY`) y enviala en cada peticion al backend: `headers['X-API-Key'] = process.env.API_RECETARIO_KEY`.
- **recetario-mcp:** Si el MCP tiene **API_KEY** definida, pon en el backend **MCP_API_KEY** con el mismo valor; el cliente MCP enviara esa cabecera al llamar al MCP.

Sin API_KEY / MCP_API_KEY los servicios siguen abiertos (solo para desarrollo).

## Levantar el backend

```bash
cd backend-alexa
node server.js
```

Puerto por defecto: **3001** (variable de entorno `PORT` si quieres otro).

No hace falta `npm install`: solo Node.js (>=18).

## Pruebas

Con el servidor levantado en otra terminal (`node server.js`):

```bash
node scripts/test-api.js
# o
npm test
```

El script llama a cada endpoint y comprueba status 200 y forma de la respuesta (recetas[], ingredientes[], menu, prices[]). Si algo falla, termina con codigo 1.

Probar contra otra URL (ej. ngrok):

```bash
BASE_URL=https://tu-url.ngrok.io node scripts/test-api.js
```

**Pruebas manuales (curl):**

```bash
curl -s http://localhost:3001/health
curl -s -X POST http://localhost:3001/api/mcp/recipes -H "Content-Type: application/json" -d '{"tipoComida":"desayuno"}'
curl -s http://localhost:3001/api/mcp/ingredients
curl -s -X POST http://localhost:3001/api/mcp/suggestions -H "Content-Type: application/json" -d '{"tiposComida":["desayuno","comida","cena"]}'
curl -s http://localhost:3001/api/mcp/prices
```

## Apuntar la skill Alexa

Lambda no puede llamar a `localhost`. Opciones:

1. **Probar en local:** `ngrok http 3001`. En la skill (Lambda): variable de entorno `API_RECETARIO_URL` = `https://TU-URL-NGROK.ngrok.io/api/mcp/recipes`.
2. **Desplegar:** Subir este backend a Railway, Render, Fly.io, etc., y usar esa URL + `/api/mcp/recipes` (y el resto de rutas) en las variables de la skill.

## Contratos (compatibles con MCP recetario-mx)

- **POST /api/mcp/recipes**  
  Body: `{ tipoComida?, ingredientes?, presupuestoDiario?, gustos?, disgustos?, objetivo? }`  
  Respuesta: `{ recetas: [ { name, description, cost, calories, ingredients } ] }`

- **GET /api/mcp/ingredients**  
  Query: `userId` (opcional)  
  Respuesta: `{ ingredientes: [ { id, name, category, unit, price } ] }`

- **POST /api/mcp/suggestions**  
  Body: `{ userId?, presupuesto?, gustos?, disgustos?, objetivo?, tiposComida? }`  
  Respuesta: `{ menu: { desayuno?, comida?, cena? } }` (cada valor: array de recetas)

- **GET /api/mcp/prices**  
  Query: `userId` (opcional)  
  Respuesta: `{ prices: [ { ingredientId, name, price, unit, store } ] }`
