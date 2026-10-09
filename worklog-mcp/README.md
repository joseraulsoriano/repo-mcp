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

Los datos nunca salen de la máquina. La base y los reportes viven fuera del repo (`~/.worklog/`).

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

Fechas aceptadas: `YYYY-MM-DD`, `hoy`, `ayer`, un día de la semana (`lunes` = el de esta semana) o `-7d`.
Por defecto el rango va del lunes de esta semana a hoy.

## CLI

```bash
uv run worklog report --since lunes --detail completo --out ~/.worklog/semana.md
uv run worklog add postura "No migrar a GraphQL" --body "REST cubre los casos" --project rtc --hours 1
uv run worklog sync --since 2026-10-01
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
