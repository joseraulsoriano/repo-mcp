# Proyectos MCP (Model Context Protocol)

Monorepo con servidores y clientes relacionados con MCP (herramientas HTTP para LLM y flujos asociados).

Licencia: ver [LICENSE](LICENSE) (MIT).

Plantilla de despliegue (URLs, riesgos): [MCP_PUBLICATION_STATUS.md](MCP_PUBLICATION_STATUS.md). Tags y releases: [RELEASING.md](RELEASING.md). Seguridad y fork: [SECURITY.md](SECURITY.md).

## Estado orientado a publicación

| Proyecto | Rol | Listo para desplegar como… | Notas |
|----------|-----|----------------------------|--------|
| [volunteer-mcp/](volunteer-mcp/) | Servidor FastAPI MCP (`/mcp/*`, `/metrics`) | Servicio HTTP (Railway, Render, Docker) | Revisar CORS en producción (`allow_origins`). Variables: ver `volunteer-mcp/.env.example`. |
| [recetario-mcp/](recetario-mcp/) | Servidor FastAPI MCP recetas/precios | Servicio HTTP | Opcional `API_KEY` para `/mcp/*` y `/tools`. Scraping de tiendas puede romperse si cambian las páginas. |
| [recetario-alexa-mcp/](recetario-alexa-mcp/) | `recetario-mcp` + `backend-alexa` (Node) | Dos servicios enlazados (`MCP_BASE_URL`, `MCP_API_KEY`) | Ver README del bundle. |
| [recetario-mx/](recetario-mx/) | App Next.js (consume `api/mcp/*`) | Producto web, no catálogo MCP | DB, NextAuth, claves propias. Integración: `src/app/api/mcp/*`, `src/utils/mcp.ts`, `MCPRunner`, `MCPShoppingOptimizer`. |
| [Kronos/](Kronos/) | API FastAPI (asistencia moto) | API de producto | Ver [Kronos/docs/PUBLICACION_MCP.md](Kronos/docs/PUBLICACION_MCP.md): no MCP catalogable hoy. |

CI: [.github/workflows/mcp-publish-smoke.yml](.github/workflows/mcp-publish-smoke.yml) construye y prueba `GET /health` y `GET /tools` en **volunteer-mcp** y **recetario-mcp**.

## Estructura del repositorio

```
mcp/
├── volunteer-mcp/          # puerto 8011
├── recetario-mcp/          # puerto 8012
├── recetario-alexa-mcp/
├── recetario-mx/
├── Kronos/
├── LICENSE
├── RELEASING.md
├── MCP_PUBLICATION_STATUS.md
└── .github/workflows/
```

## Qué es MCP (resumen)

MCP permite exponer herramientas y contexto estructurado a clientes de modelos de lenguaje. Aquí los servidores “MCP” del hackathon/producto exponen principalmente **HTTP + JSON** (POST `/mcp/...`), no necesariamente el transporte stdio del CLI oficial.

## Requisitos y documentación

Cada carpeta tiene su propio README: dependencias Python/Node, Docker, variables de entorno (plantillas `.env.example` donde aplica).

## Tecnologías

- **Backend MCP:** Python (FastAPI), Uvicorn, Docker
- **Web:** Next.js, TypeScript, Prisma, Tailwind
- **Datos:** SQLite, PostgreSQL, Redis (opcional)
- **Externas:** Brave Search API, Google Maps (recetario-mx)
