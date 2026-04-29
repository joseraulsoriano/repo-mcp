/**
 * Backend Recetario MX para la skill Alexa.
 * Arquitectura modular por secciones (recetas, ingredientes, sugerencias, precios/compras).
 * Apunta al mismo contrato que el MCP de recetario-mx.
 */
const http = require('http');
const { parseBody } = require('./lib/parseBody');
const { send } = require('./lib/response');
const auth = require('./lib/auth');
const recipes = require('./routes/recipes');
const ingredients = require('./routes/ingredients');
const suggestions = require('./routes/suggestions');
const prices = require('./routes/prices');
const health = require('./routes/health');

const PORT = process.env.PORT || 3001;

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization');
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') {
    cors(res);
    res.writeHead(204);
    res.end();
    return;
  }

  const url = req.url || '';
  const path = url.split('?')[0];

  if (path.startsWith('/api/mcp/') && auth.isProtected() && !auth.isValid(req)) {
    send(res, 401, { error: 'Unauthorized' });
    return;
  }

  try {
    if (req.method === 'POST' && path === '/api/mcp/recipes') {
      const body = await parseBody(req);
      await recipes.handleRecipes(body, res);
      return;
    }
    if (req.method === 'GET' && path === '/api/mcp/ingredients') {
      await ingredients.handleGet(req, res);
      return;
    }
    if (req.method === 'POST' && path === '/api/mcp/ingredients') {
      const body = await parseBody(req);
      ingredients.handlePost(body, res);
      return;
    }
    if (req.method === 'POST' && path === '/api/mcp/suggestions') {
      const body = await parseBody(req);
      await suggestions.handleSuggestions(body, res);
      return;
    }
    if (req.method === 'GET' && path === '/api/mcp/prices') {
      await prices.handlePrices(req, res);
      return;
    }
    if (req.method === 'GET' && (path === '/' || path === '/health')) {
      health.handleHealth(res);
      return;
    }
  } catch (e) {
    send(res, 400, { error: 'Peticion invalida' });
    return;
  }

  send(res, 404, { error: 'Not found' });
});

server.listen(PORT, () => {
  const mcp = process.env.MCP_BASE_URL ? 'recetario-mcp (' + process.env.MCP_BASE_URL + ')' : 'demo';
  const protected_ = auth.isProtected() ? 'X-API-Key / Authorization requeridos en /api/mcp/*' : 'sin API key';
  console.log('Recetario MX backend (Alexa) en http://localhost:' + PORT);
  console.log('  Origen datos: ' + mcp + ' | Proteccion: ' + protected_);
  console.log('  POST /api/mcp/recipes     -> recetas (tipoComida: desayuno, comida, cena)');
  console.log('  GET  /api/mcp/ingredients -> listar (?q=, ?userId=)');
  console.log('  POST /api/mcp/ingredients -> anadir ingrediente');
  console.log('  POST /api/mcp/suggestions -> menu del dia (tiposComida)');
  console.log('  GET  /api/mcp/prices      -> precios (?q=, ?userId=)');
  console.log('  GET  /health              -> estado del servicio');
});
