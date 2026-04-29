# Listo para GitHub

Este repo contiene solo **recetario-mcp** y **backend-alexa** (no el resto de PROGRAMMING ni LIFE OF CHASSE).

## Antes de subir

- [ ] No hay archivos `.env` en el repo (el `.gitignore` raiz los ignora; si copiaste, `.env` de recetario-mcp no se subira).
- [ ] Cada carpeta tiene su `.env.example` (recetario-mcp y backend-alexa) para documentar variables.
- [ ] No hay claves hardcodeadas en el codigo.
- [ ] README raiz explica las dos partes y el flujo Alexa -> backend-alexa -> recetario-mcp.

## Estructura que se sube

```
recetario-alexa-mcp/
  README.md
  .gitignore
  GITHUB_READY.md
  recetario-mcp/     # Motor MCP (Python)
  backend-alexa/     # Backend Alexa (Node)
```

## Primer push

1. Entra en la carpeta: `cd recetario-alexa-mcp`
2. `git init`
3. `git add .`
4. `git status` (comprueba que no aparezca `.env`)
5. `git commit -m "recetario-mcp + backend-alexa"`
6. Crea el repo en GitHub y enlaza: `git remote add origin <url>`
7. `git push -u origin main`
