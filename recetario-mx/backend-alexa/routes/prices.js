/**
 * Rutas: Precios / Compras (MCP /api/mcp/prices).
 * GET: si MCP_BASE_URL está definido, llama a recetario-mcp (prices_search); si no, datos demo.
 */
const { send } = require('../lib/response');
const { getPrices } = require('../data/prices');
const { isConfigured, callMcp } = require('../lib/mcpClient');
const { mapPreciosFromMcp } = require('../lib/mapMcp');

async function handlePrices(req, res) {
  const url = new URL(req.url || '', `http://${req.headers.host}`);
  const userId = url.searchParams.get('userId') || null;
  const query = url.searchParams.get('q') || url.searchParams.get('query') || 'precios supermercado mexico';

  if (isConfigured()) {
    try {
      const out = await callMcp('recetario.prices_search', {
        query,
        scraping: true,
        topK: 10
      });
      if (!out.success) {
        send(res, 502, { error: out.error || 'MCP error', prices: getPrices(userId) });
        return;
      }
      const prices = mapPreciosFromMcp(out.result).map(p => ({ ...p, userId }));
      send(res, 200, { prices });
      return;
    } catch (e) {
      send(res, 502, { error: String(e.message || e), prices: getPrices(userId) });
      return;
    }
  }

  send(res, 200, { prices: getPrices(userId) });
}

module.exports = { handlePrices };
