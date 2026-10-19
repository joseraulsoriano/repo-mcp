# worklog-mcp

Bitácora personal de trabajo construida a partir de las sesiones de Claude Code: horas activas,
qué se pidió, qué se entregó, archivos tocados, revisiones (skills como `/review`, `/cso`,
`/code-review`), commits y entradas manuales para lo que no queda en el código
(revisiones, análisis, posturas, decisiones, reuniones).

Pensado como evidencia de trabajo: un "Jira personal" que se lee en dos minutos.

## Cómo funciona

1. Lee los transcripts de `~/.claude/projects/**.jsonl` (incluidos los de subagentes).
2. Los indexa en SQLite en `~/.worklog/worklog.db`. Sólo re-parsea los archivos que cambiaron.
3. Cruza con `git log --all` de cada repo donde hubo sesiones.
4. Genera Markdown por **día → proyecto → sesión**.

Los datos no salen de la máquina salvo que configures `worklog publish` (ver abajo). La base y los reportes viven fuera del repo (`~/.worklog/`).

**Horas activas** = suma de los intervalos entre eventos de la sesión separados por ≤ 15 min.
Si hay varias sesiones en paralelo, el tiempo se cuenta una sola vez. Incluye el tiempo en que el
agente trabajó solo (sesiones `bg`). El umbral se cambia con `WORKLOG_IDLE_MINUTES`.

## Instalación como MCP en Claude Code

```bash
claude mcp add worklog --scope user -- \
  uv run --directory "/ruta/a/mcp/worklog-mcp" worklog-mcp
```

Luego, en cualquier sesión: *"dame mi bitácora desde el lunes"*, *"registra una postura: …"*.

## Herramientas

| Tool | Para qué |
|---|---|
| `worklog_report(since, until, project, detail, save_to)` | Bitácora en Markdown. `detail`: `breve` o `completo`. |
| `worklog_sessions(since, until, project)` | Lista compacta de sesiones con id y horas. |
| `worklog_session(session_id)` | Detalle de una sesión: todas las instrucciones, acciones y entregables. |
| `worklog_add_entry(kind, title, body, project, hours, day)` | Registro manual: `revision`, `analisis`, `postura`, `decision`, `reunion`, `nota`, `entrega`. |
| `worklog_entries` / `worklog_delete_entry` | Consultar o borrar entradas manuales. |
| `worklog_search(query, since)` | Busca en instrucciones, entregables y entradas. |
| `worklog_sync(since)` | Fuerza la reindexación. |
| `worklog_jira_sync(since, until, dry_run)` | Avisa a Jira del trabajo hecho, sólo en tareas asignadas a ti (ver abajo). |
| `worklog_jira_close(key, note)` | Cierra una tarea tuya con una nota. |

Fechas aceptadas: `YYYY-MM-DD`, `hoy`, `ayer`, un día de la semana (`lunes` = el de esta semana) o `-7d`.
Por defecto el rango va del lunes de esta semana a hoy.

## CLI

```bash
uv run worklog report --since lunes --detail completo --out ~/.worklog/semana.md
uv run worklog add postura "No migrar a GraphQL" --body "REST cubre los casos" --project rtc --hours 1
uv run worklog sync --since 2026-10-01
uv run worklog snapshot   # escribe ~/.worklog/hoy.md, semana.md y semanas/<lunes>.md
```

## Panel en RTC Soluciones (`/admin/bitacora`)

`worklog publish` manda un resumen por día al panel, que lo analiza contra metas (horas por día,
sesiones con entregable, foco, ramas fuera de main/test, días sin registro). Es la única vía por
la que algo sale de la máquina, y sólo si lo configuras:

```bash
export WORKLOG_PANEL_URL=https://rtcsoluciones.mx   # o http://localhost:4321
export WORKLOG_PANEL_TOKEN=...                      # el mismo valor que BITACORA_TOKEN del panel
uv run worklog publish --since=-30d                 # el = es necesario con fechas negativas
```

O, para que el token no quede en texto plano en ningún archivo, en el Llavero de macOS y sólo la
URL en `~/.worklog/panel.json` (que es lo que lee el hook):

```bash
security add-generic-password -s worklog-panel -a "$USER" -w   # pide el token sin mostrarlo
echo '{"url": "https://rtcsoluciones.mx"}' > ~/.worklog/panel.json
```

El JSON también acepta `"token"`, pero el Llavero gana si existen los dos. Con
eso configurado, `snapshot` publica también hoy y ayer al cerrar cada sesión. Desde Claude Code:
herramienta `worklog_publish`. Reenviar es seguro: cada día reemplaza al anterior.

No viajan los comandos de shell ni las instrucciones completas (sólo la primera de cada sesión,
recortada a 300 caracteres).

## Jira: avisar de tu trabajo, sólo en tareas tuyas

`worklog jira` (y la herramienta `worklog_jira_sync`) cruza las sesiones con Jira y avisa del
trabajo hecho. Regla **«sólo sí»**: una sesión se vincula a una tarea únicamente si

1. su clave (`QYCA-15`) aparece donde hay intención de trabajarla: la **rama**, un **commit hecho
   en la sesión** o la **primera instrucción** de la sesión (una mención de pasada no cuenta), y
2. Jira confirma que la tarea **existe** y su responsable **eres tú**.

Si no se cumple, no se toca nada: la tarea sale en `omitidas` con el motivo («no está asignada a
ti», «no existe») y la sesión en `sin_tarea`, con sus horas, para que se vea qué trabajo no está en
Jira (por ejemplo, la web de otro sistema que nadie dio de alta).

Con cada tarea vinculada:

- **Por hacer → En curso** al detectar trabajo. Nunca reabre una tarea terminada.
- **→ Listo** sólo con una señal explícita en una instrucción o en un commit de la sesión:
  «cierra QYCA-15», «closes QYCA-15», «QYCA-15 listo». O a mano: `worklog_jira_close`.
- **Un comentario por sesión** con fecha, horas, entregables y número de archivos; si la sesión
  sigue, se actualiza el mismo comentario.

Los commits de `git log` no cuentan por sí solos: en repos compartidos traen los de otras personas.

```bash
uv run worklog jira --configure          # URL, correo y API token; los prueba y guarda el token en el Llavero
uv run worklog jira --dry-run            # qué haría con ayer y hoy, sin tocar Jira
uv run worklog jira --since lunes        # lo hace
uv run worklog jira --close QYCA-16 --note "Entregado al cliente"
```

No uses `security add-generic-password … -w` a mano: su aviso recorta la entrada a 128 caracteres
y los API tokens de Atlassian son más largos, así que se guarda roto y Jira responde 401.

Con eso configurado, `snapshot` (hook `SessionEnd`) sincroniza ayer y hoy al cerrar cada sesión y
deja el resumen en `~/.worklog/jira.md`. A Jira viajan el título de la sesión, sus entregables y el
número de archivos; nunca los comandos ni las instrucciones completas.

## Automático al cerrar sesión

`snapshot` está pensado para un hook `SessionEnd` en `~/.claude/settings.json`: tarda menos de
un segundo, no imprime nada y, si algo falla, lo anota en `~/.worklog/hook.log` en lugar de
romper el cierre de la sesión. `semanas/<lunes>.md` queda como archivo histórico de cada semana.

```json
"hooks": {
  "SessionEnd": [{ "hooks": [{ "type": "command", "timeout": 30,
    "command": "uv run --directory \"/ruta/a/mcp/worklog-mcp\" worklog snapshot" }] }]
}
```

## Qué cuenta como entregable

- Líneas `result: …` que el agente escribe al cerrar una tarea.
- Archivos editados con `Edit`/`Write` (se omiten temporales de `~/.claude/jobs/*/tmp` y `/tmp`).
- Comandos con huella: `git commit/push/merge/tag`, `gh pr create/merge`, deploys.
- Skills invocadas y hallazgos reportados (revisiones).

## Tests

```bash
uv run pytest -q
```
