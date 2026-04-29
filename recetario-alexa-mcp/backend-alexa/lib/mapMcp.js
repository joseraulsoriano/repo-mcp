/**
 * Mapea respuestas de recetario-mcp al formato que espera backend-alexa / Lambda.
 * MCP devuelve title/url/snippet; backend espera name/description/ingredients/cost.
 */
function mapRecetasFromMcp(mcpResult) {
  const list = (mcpResult && mcpResult.recetas) || [];
  return list.map((r, i) => ({
    name: r.title || `Receta ${i + 1}`,
    description: r.snippet || '',
    cost: null,
    ingredients: [],
    url: r.url || null
  }));
}

function mapIngredientesFromMcp(mcpResult) {
  const list = (mcpResult && mcpResult.ingredientes) || [];
  return list.map((r, i) => ({
    id: String(i + 1),
    name: r.title || `Ingrediente ${i + 1}`,
    category: 'GENERAL',
    unit: 'unidad',
    price: null,
    url: r.url || null
  }));
}

function mapPreciosFromMcp(mcpResult) {
  const list = (mcpResult && mcpResult.precios) || [];
  return list.map((p, i) => ({
    ingredientId: String(i + 1),
    name: p.title || `Producto ${i + 1}`,
    price: p.price != null ? p.price : null,
    unit: 'unidad',
    store: p.store || 'Otro',
    url: p.url || null
  }));
}

module.exports = { mapRecetasFromMcp, mapIngredientesFromMcp, mapPreciosFromMcp };
