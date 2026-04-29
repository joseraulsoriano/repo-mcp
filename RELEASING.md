# Releases y tags (MCP)

Antes de etiquetar, conviene que pase el workflow **MCP publish smoke** en la rama principal y, si aplica, `pnpm build` en `recetario-mx`.

## Checklist corto

1. Actualizar [MCP_PUBLICATION_STATUS.md](MCP_PUBLICATION_STATUS.md) con URLs reales de produccion (sin secretos).
2. Confirmar que no hay `.env` ni claves en el commit.
3. Ejecutar smoke local o confiar en CI: [.github/workflows/mcp-publish-smoke.yml](.github/workflows/mcp-publish-smoke.yml).

## Tags git sugeridos (por servicio)

Desde la raiz del monorepo, con `main` actualizado:

```bash
git checkout main
git pull

git tag -a volunteer-mcp-v1.0.0 -m "volunteer-mcp: smoke Docker + health/tools"
git tag -a recetario-mcp-v1.0.0 -m "recetario-mcp: smoke Docker + health/tools"

git push origin volunteer-mcp-v1.0.0 recetario-mcp-v1.0.0
```

Ajusta el prefijo de version (`v1.0.1`, etc.) segun tus reglas del proyecto. Los tags no despliegan solos: enlazalos en Railway, Render, Docker Hub, etc.

## Imagen Docker (opcional)

Si publicas en un registry, construye desde el directorio del servicio:

```bash
docker build -t tu-registry/volunteer-mcp:1.0.0 volunteer-mcp
docker build -t tu-registry/recetario-mcp:1.0.0 recetario-mcp
```

## Kronos y recetario-mx

- **Kronos:** publicar como API; ver [Kronos/docs/VERIFICACION.md](Kronos/docs/VERIFICACION.md) y [Kronos/docs/PUBLICACION_MCP.md](Kronos/docs/PUBLICACION_MCP.md) (no es paquete MCP de catalogo hoy).
- **recetario-mx:** app Next.js; tag opcional `recetario-mx-v1.0.0` si versionas el front aparte.
