# Estado de publicacion MCP (plantilla operativa)

Rellena URLs y fechas cuando despliegues. No incluyas secretos en este archivo. Para tags Git: [RELEASING.md](RELEASING.md).

| Proyecto | Estado smoke | Smoke local / CI | URL produccion (opcional) | Variables obligatorias en prod | Riesgos |
|----------|--------------|------------------|---------------------------|-------------------------------|---------|
| volunteer-mcp | OK en CI | `.github/workflows/mcp-publish-smoke.yml` + [volunteer-mcp/README.md](volunteer-mcp/README.md) | | `BRAVE_API_KEY` recomendada; opcional `REDIS_URL`, `DATABASE_URL` | CORS `*`; cuota Brave |
| recetario-mcp | OK en CI | mismo workflow + [recetario-mcp/README.md](recetario-mcp/README.md) | | `BRAVE_API_KEY` recomendada; opcional `API_KEY` | Scraping tiendas frágil |
| recetario-alexa-mcp (2 servicios) | Manual | README [recetario-alexa-mcp/README.md](recetario-alexa-mcp/README.md); `backend-alexa/.env.example` | MCP: ___ / Backend: ___ | MCP: como recetario-mcp; Backend: `MCP_BASE_URL`, opcional `MCP_API_KEY`, `API_KEY` | Dos despliegues a coordinar |
| recetario-mx | Manual | `cd recetario-mx && pnpm install && pnpm build` | | `DATABASE_URL`, `NEXTAUTH_SECRET`, etc. | No es servidor MCP; app web |
| Kronos | Manual / Docker | [Kronos/docs/VERIFICACION.md](Kronos/docs/VERIFICACION.md) | | Segun despliegue | **No** es MCP publicable hoy ([PUBLICACION_MCP.md](Kronos/docs/PUBLICACION_MCP.md)) |

## Secretos

- Nunca commitear `.env`. Usar `.env.example` por proyecto.
- Rotar claves si alguna se filtro en historial git.

## Versionado sugerido

- Tag git por servicio publicable, ej. `volunteer-mcp-v1.0.0`, `recetario-mcp-v1.0.0`.
