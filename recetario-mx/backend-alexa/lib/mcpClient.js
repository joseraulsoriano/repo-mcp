/**
 * Cliente para llamar a recetario-mcp (MCP_BASE_URL).
 * POST a /mcp/recetario.<tool> con body JSON; devuelve result o lanza.
 */
const baseUrl = () => process.env.MCP_BASE_URL || '';

function isConfigured() {
  const url = baseUrl();
  return typeof url === 'string' && url.length > 0;
}

/**
 * Llama a una tool del MCP.
 * @param {string} toolPath - Ej: "recetario.recipes_search"
 * @param {object} params - Body del POST (query, tipo_comida, etc.)
 * @returns {Promise<object>} result del MCP (success: true) o { success: false, error }
 */
async function callMcp(toolPath, params = {}) {
  const base = baseUrl().replace(/\/$/, '');
  const path = toolPath.startsWith('/') ? toolPath : `/mcp/${toolPath}`;
  const url = `${base}${path}`;

  const headers = { 'Content-Type': 'application/json' };
  const mcpKey = process.env.MCP_API_KEY || '';
  if (mcpKey.length > 0) headers['X-API-Key'] = mcpKey;

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(params)
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    return { success: false, error: data.detail || data.error || res.statusText };
  }
  if (data.success === false) {
    return { success: false, error: data.error || 'MCP error' };
  }
  return { success: true, result: data.result || data };
}

module.exports = { isConfigured, callMcp };
