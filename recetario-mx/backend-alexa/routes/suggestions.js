/**
 * Rutas: Sugerencias / Menu del dia (MCP /api/mcp/suggestions).
 * Si MCP_BASE_URL está definido, llama a recetario-mcp por cada tipo (desayuno, comida, cena); si no, datos demo.
 */
const { send } = require('../lib/response');
const { getMenu } = require('../data/suggestions');
const { isConfigured, callMcp } = require('../lib/mcpClient');
const { mapRecetasFromMcp } = require('../lib/mapMcp');

async function handleSuggestions(body, res) {
  const tiposComida = Array.isArray(body.tiposComida) ? body.tiposComida : ['desayuno', 'comida', 'cena'];

  if (isConfigured()) {
    try {
      const menu = {};
      for (const t of tiposComida) {
        const tipo = ['desayuno', 'comida', 'cena'].includes(t) ? t : t.toLowerCase();
        const out = await callMcp('recetario.recipes_search', {
          query: 'recetas mexicanas',
          tipo_comida: tipo,
          topK: 5
        });
        menu[tipo] = out.success ? mapRecetasFromMcp(out.result) : [];
      }
      send(res, 200, { menu });
      return;
    } catch (e) {
      send(res, 502, { error: String(e.message || e), menu: getMenu(tiposComida) });
      return;
    }
  }

  send(res, 200, { menu: getMenu(tiposComida) });
}

module.exports = { handleSuggestions };
