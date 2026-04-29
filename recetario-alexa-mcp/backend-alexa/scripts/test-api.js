/**
 * Pruebas de los endpoints del backend (sin dependencias).
 * Ejecutar con el servidor levantado: node server.js (en otra terminal).
 *
 *   node scripts/test-api.js
 *   BASE_URL=https://tu-ngrok.ngrok.io node scripts/test-api.js
 */
const http = require('http');
const https = require('https');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';

function request(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const isHttps = url.protocol === 'https:';
    const lib = isHttps ? https : http;
    const options = {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname + url.search,
      method,
      headers: body ? { 'Content-Type': 'application/json' } : {}
    };
    const req = lib.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: data ? JSON.parse(data) : {} });
        } catch (e) {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

function ok(name, condition, detail = '') {
  const pass = !!condition;
  console.log(pass ? '  OK' : '  FAIL', name, detail ? `(${detail})` : '');
  return pass;
}

async function run() {
  console.log('Pruebas backend Recetario MX');
  console.log('BASE_URL:', BASE_URL);
  console.log('');

  let passed = 0;
  let failed = 0;

  try {
    const health = await request('GET', '/health');
    if (ok('GET /health -> 200', health.status === 200) && ok('GET /health -> ok: true', health.body.ok === true)) passed++; else failed++;
  } catch (e) {
    console.log('  FAIL GET /health', e.message);
    failed++;
  }

  try {
    const recipes = await request('POST', '/api/mcp/recipes', { tipoComida: 'desayuno' });
    const recetas = recipes.body.recetas || [];
    if (ok('POST /api/mcp/recipes -> 200', recipes.status === 200) && ok('POST /api/mcp/recipes -> recetas[]', Array.isArray(recetas) && recetas.length > 0)) passed++; else failed++;
  } catch (e) {
    console.log('  FAIL POST /api/mcp/recipes', e.message);
    failed++;
  }

  try {
    const ingredients = await request('GET', '/api/mcp/ingredients');
    const ingredientes = ingredients.body.ingredientes || [];
    if (ok('GET /api/mcp/ingredients -> 200', ingredients.status === 200) && ok('GET /api/mcp/ingredients -> ingredientes[]', Array.isArray(ingredientes) && ingredientes.length > 0)) passed++; else failed++;
  } catch (e) {
    console.log('  FAIL GET /api/mcp/ingredients', e.message);
    failed++;
  }

  try {
    const suggestions = await request('POST', '/api/mcp/suggestions', { tiposComida: ['desayuno', 'comida', 'cena'] });
    const menu = suggestions.body.menu || {};
    const hasMenu = menu.desayuno && menu.comida && menu.cena;
    if (ok('POST /api/mcp/suggestions -> 200', suggestions.status === 200) && ok('POST /api/mcp/suggestions -> menu', hasMenu)) passed++; else failed++;
  } catch (e) {
    console.log('  FAIL POST /api/mcp/suggestions', e.message);
    failed++;
  }

  try {
    const prices = await request('GET', '/api/mcp/prices');
    const pricesList = prices.body.prices || [];
    if (ok('GET /api/mcp/prices -> 200', prices.status === 200) && ok('GET /api/mcp/prices -> prices[]', Array.isArray(pricesList) && pricesList.length > 0)) passed++; else failed++;
  } catch (e) {
    console.log('  FAIL GET /api/mcp/prices', e.message);
    failed++;
  }

  console.log('');
  console.log('Resultado:', passed, 'pasaron,', failed, 'fallaron');
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
