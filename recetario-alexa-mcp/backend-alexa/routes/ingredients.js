/**
 * Rutas: Ingredientes (MCP /api/mcp/ingredients).
 * GET: si MCP_BASE_URL está definido, llama a recetario-mcp; si no, datos demo.
 * POST: demo en memoria (MCP no tiene alta de ingredientes).
 */
const { send } = require('../lib/response');
const { listIngredientes } = require('../data/ingredients');
const { isConfigured, callMcp } = require('../lib/mcpClient');
const { mapIngredientesFromMcp } = require('../lib/mapMcp');

async function handleGet(req, res) {
  const url = new URL(req.url || '', `http://${req.headers.host}`);
  const userId = url.searchParams.get('userId') || null;

  if (isConfigured()) {
    try {
      const query = url.searchParams.get('q') || url.searchParams.get('query') || 'ingredientes cocina mexicana';
      const out = await callMcp('recetario.ingredients_search', { query, topK: 15 });
      if (!out.success) {
        send(res, 502, { error: out.error || 'MCP error', ingredientes: listIngredientes(userId) });
        return;
      }
      const ingredientes = mapIngredientesFromMcp(out.result).map(i => ({ ...i, userId }));
      send(res, 200, { ingredientes });
      return;
    } catch (e) {
      send(res, 502, { error: String(e.message || e), ingredientes: listIngredientes(userId) });
      return;
    }
  }

  send(res, 200, { ingredientes: listIngredientes(userId) });
}

function handlePost(body, res) {
  if (!body.ingredient && !body.name) {
    send(res, 400, { error: 'Se requiere ingredient o name', ingredientes: listIngredientes() });
    return;
  }
  const ing = body.ingredient || { name: body.name, category: body.category || 'VERDURAS', unit: body.unit || 'kg', price: body.price || 0 };
  send(res, 201, { ingredientes: listIngredientes().concat([{ id: String(Date.now()), ...ing }]) });
}

module.exports = { handleGet, handlePost };
