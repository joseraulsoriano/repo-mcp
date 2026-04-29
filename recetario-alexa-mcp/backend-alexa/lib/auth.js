/**
 * Validacion de API key para proteger el backend.
 * Si API_KEY esta definida, las rutas /api/mcp/* requieren cabecera X-API-Key o Authorization: Bearer <key>.
 */
function getApiKey() {
  return process.env.API_KEY || '';
}

function isProtected() {
  return getApiKey().length > 0;
}

/**
 * Extrae la key de la peticion: X-API-Key o Authorization: Bearer <key>.
 * @param {import('http').IncomingMessage} req
 * @returns {string}
 */
function keyFromRequest(req) {
  const header = req.headers && (req.headers['x-api-key'] || req.headers['authorization']);
  if (!header || typeof header !== 'string') return '';
  if (header.toLowerCase().startsWith('bearer ')) return header.slice(7).trim();
  return header.trim();
}

/**
 * Devuelve true si la peticion tiene una key valida (o si no hay proteccion).
 * @param {import('http').IncomingMessage} req
 * @returns {boolean}
 */
function isValid(req) {
  if (!isProtected()) return true;
  const key = getApiKey();
  const provided = keyFromRequest(req);
  return provided.length > 0 && provided === key;
}

module.exports = { getApiKey, isProtected, keyFromRequest, isValid };
