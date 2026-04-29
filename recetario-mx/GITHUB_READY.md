# Listo para GitHub - Recetario MX

Revisa antes de subir el repo.

## .gitignore

- [ ] No se sube `.env` ni archivos con claves (`.env`, `.env.local`, etc.).
- [ ] `.env.example` si se sube (plantilla sin valores secretos).
- [ ] `node_modules/`, `.next/`, `build/` ignorados.
- [ ] `backend-alexa/` no tiene `.env`; tiene `.env.example` para documentar variables.

## Documentacion

- [ ] **README.md** (raiz): descripcion del proyecto, Next.js, backend-alexa, Alexa.
- [ ] **backend-alexa/README.md**: endpoints, MCP_BASE_URL, API_KEY, despliegue.
- [ ] **ALEXA_SETUP.md**: configuracion de la skill (nombre, intents, endpoint).
- [ ] **DATA_LAYER.md**: DynamoDB single-table y curación (opcional).

## Codigo

- [ ] No hay claves ni secrets hardcodeados (solo `process.env.*`).
- [ ] Variables sensibles (DATABASE_URL, NEXTAUTH_SECRET, API keys) solo en `.env` (no en repo).
- [ ] backend-alexa: `node server.js` arranca; rutas `/api/mcp/*` y `/health` responden.

## Opcional antes del primer push

- [ ] `npm run build` en la raiz sin errores.
- [ ] `npm run lint` sin errores.
- [ ] Si usas Prisma: migraciones en `prisma/migrations/`; no subir `.env` con DATABASE_URL real.

## Repositorios recomendados

- **recetario-mx**: este repo (Next.js + backend-alexa en una sola raiz). En Render puedes usar Root Directory `backend-alexa` para el Web Service del backend.
- **recetario-mcp**: repo aparte (solo el motor MCP en Python). Ver `recetario-mcp/GITHUB_READY.md`.
