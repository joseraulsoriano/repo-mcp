/**
 * Rutas: Salud del servicio.
 * GET /health -> estado del backend.
 */
const { send } = require('../lib/response');

const SERVICE = 'recetario-mx-backend-alexa';
const VERSION = '1.0.0';

function handleHealth(res) {
  send(res, 200, { ok: true, service: SERVICE, version: VERSION });
}

module.exports = { handleHealth };
