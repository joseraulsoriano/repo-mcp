/**
 * Rutas: Recetas (MCP /api/mcp/recipes).
 * Si MCP_BASE_URL está definido, llama a recetario-mcp; si no, usa datos demo.
 */
const { send } = require('../lib/response');
const { getRecetas } = require('../data/recipes');
const { isConfigured, callMcp } = require('../lib/mcpClient');
const { mapRecetasFromMcp } = require('../lib/mapMcp');

async function handleRecipes(body, res) {
  const tipoComida = (body.tipoComida || 'comida').toLowerCase().trim();

  if (isConfigured()) {
    try {
      const out = await callMcp('recetario.recipes_search', {
        query: 'recetas mexicanas',
        tipo_comida: tipoComida,
        topK: 10
      });
      if (!out.success) {
        send(res, 502, { error: out.error || 'MCP error', recetas: getRecetas(tipoComida) });
        return;
      }
      const recetas = mapRecetasFromMcp(out.result);
      send(res, 200, { recetas });
      return;
    } catch (e) {
      send(res, 502, { error: String(e.message || e), recetas: getRecetas(tipoComida) });
      return;
    }
  }

  const recetas = getRecetas(tipoComida);
  send(res, 200, { recetas });
}

module.exports = { handleRecipes };
