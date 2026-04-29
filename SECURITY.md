# Seguridad del repositorio

## Secretos

- No subas archivos `.env`; usa solo `.env.example` con valores ficticios.
- Si alguna clave llegó a estar en Git o en un fork público, **rótala** en el proveedor (Brave, etc.) y actualiza despliegues.

## Código y servicios

- Los MCP en modo desarrollo pueden ir **sin `API_KEY`**. En Internet, define `API_KEY` / `MCP_API_KEY` como documentan los README.
- **CORS `*`** en volunteer-mcp / recetario-mcp es cómodo en local; en producción conviene limitar orígenes.

## GitHub: fork vs clone vs “solo fork”

- Un repositorio **público** puede ser **clonado** y **forkeado** por cualquiera. Git/GitHub **no** ofrece “solo fork, no clone”: el contenido es el mismo.
- Para **restringir quién ve el código**: repo **privado** + colaboradores, o GitHub Enterprise con políticas de organización.
- Desde terminal puedes gestionar el repo remoto con **GitHub CLI**:

```bash
gh auth login
gh repo edit OWNER/REPO --visibility private   # o public
```

No existe un flag del tipo “solo permitir fork”. Lo habitual es: repo privado (sin fork público) o público (todo el mundo puede clonar y forkar).

## Comprobar que `.env` no se sube

```bash
git status
git check-ignore -v ruta/al/.env
```

Si `.env` ya se commiteó antes, hay que sacarlo del historial (`git filter-repo` o soporte de GitHub) además de borrar el archivo.
