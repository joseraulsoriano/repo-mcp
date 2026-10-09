"""Servidor MCP (stdio) de la bitácora de trabajo."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from . import publish, report, store

mcp = MCPServer(
    "worklog",
    instructions=(
        "Bitácora personal de trabajo construida desde las sesiones de Claude Code y git. "
        "Usa worklog_report para resúmenes por rango (por defecto, desde el lunes de esta semana), "
        "worklog_session para el detalle de una sesión y worklog_add_entry para dejar registro de "
        "revisiones, análisis, posturas o decisiones que no quedan en el código. "
        "Fechas: YYYY-MM-DD, 'hoy', 'ayer', un día de la semana ('lunes') o '-7d'."
    ),
)


def _range(since: str | None, until: str | None) -> tuple[date, date]:
    start = report.parse_day(since, report.this_monday())
    end = report.parse_day(until)
    if end < start:
        raise ValueError("until es anterior a since")
    return start, end


def _synced(start: date):
    con = store.connect()
    store.sync(con, start)
    return con


@mcp.tool()
def worklog_sync(since: str | None = None) -> dict:
    """Reindexa los transcripts de Claude Code modificados desde `since` (por defecto el lunes)."""
    start, _ = _range(since, None)
    with store.connect() as con:
        return store.sync(con, start)


@mcp.tool()
def worklog_publish(since: str | None = "-6d", until: str | None = None) -> dict:
    """Manda los días [since, until] al panel de RTC Soluciones (/admin/bitacora).

    Reenviar es seguro: cada día reemplaza al anterior. Necesita WORKLOG_PANEL_URL y
    WORKLOG_PANEL_TOKEN, o ~/.worklog/panel.json con url y token.
    """
    start, end = _range(since or "-6d", until)
    with store.connect() as con:
        return publish.publish(con, start, end)


@mcp.tool()
def worklog_report(since: str | None = None, until: str | None = None, project: str | None = None,
                   detail: str = "breve", save_to: str | None = None) -> str:
    """Bitácora en Markdown por día → proyecto → sesión: horas activas, instrucciones, entregables,
    archivos, revisiones (skills), commits y entradas manuales.

    detail: "breve" (una línea por sesión) o "completo" (prompts, archivos, comandos).
    save_to: ruta opcional donde guardar el .md (por defecto no guarda).
    """
    start, end = _range(since, until)
    con = _synced(start)
    md = report.render(report.collect(con, start, end, project), detail)
    if save_to:
        path = Path(save_to).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        md += f"\n\n_Guardado en `{path}`._"
    return md


@mcp.tool()
def worklog_sessions(since: str | None = None, until: str | None = None, project: str | None = None) -> list[dict]:
    """Lista compacta de sesiones con id, proyecto, título, horas y número de instrucciones."""
    start, end = _range(since, until)
    data = report.collect(_synced(start), start, end, project)
    rows = []
    for day in data["days"]:
        for name, p in day["projects"].items():
            for s in p["sessions"]:
                rows.append({"day": day["day"].isoformat(), "session_id": s["session_id"], "project": name,
                             "title": s["title"], "start": f"{s['start']:%H:%M}", "end": f"{s['end']:%H:%M}",
                             "hours": round(s["hours"], 2), "prompts": len(s["prompts"]),
                             "files": len(s["files"]), "results": s["results"][-1:]})
    return rows


@mcp.tool()
def worklog_session(session_id: str) -> dict:
    """Detalle completo de una sesión (acepta prefijo del id): instrucciones, acciones y entregables."""
    con = store.connect()
    rows = con.execute("SELECT * FROM sessions WHERE session_id LIKE ? ORDER BY is_subagent",
                       (session_id + "%",)).fetchall()
    if not rows:
        return {"error": f"No hay sesión indexada con id {session_id!r}. Corre worklog_sync con un rango mayor."}
    sid = rows[0]["session_id"]
    main = dict(rows[0])
    stamps = [store.from_iso(r["ts"]) for r in con.execute(
        "SELECT a.ts FROM activity a JOIN sessions s ON s.source=a.source WHERE s.session_id=?",
        (sid,))]
    return {
        "session_id": sid, "project": main["project"], "cwd": main["cwd"], "title": main["title"],
        "branch": main["git_branch"], "kind": main["kind"],
        "start": store.from_iso(main["first_ts"]).isoformat(), "end": store.from_iso(main["last_ts"]).isoformat(),
        "active_hours": round(store.active_hours(stamps), 2),
        "subagents": len(rows) - 1,
        "lines_added": sum(r["lines_added"] or 0 for r in rows),
        "lines_removed": sum(r["lines_removed"] or 0 for r in rows),
        "prompts": [{"ts": store.from_iso(r["ts"]).strftime("%Y-%m-%d %H:%M"), "text": r["text"]}
                    for r in con.execute("SELECT ts, text FROM prompts WHERE session_id=? ORDER BY ts", (sid,))],
        "actions": [{"ts": store.from_iso(r["ts"]).strftime("%Y-%m-%d %H:%M"), "kind": r["kind"], "target": r["target"]}
                    for r in con.execute("SELECT ts, kind, target FROM actions WHERE session_id=? ORDER BY ts", (sid,))],
        "last_message": main["last_text"],
    }


@mcp.tool()
def worklog_add_entry(kind: str, title: str, body: str = "", project: str = "", hours: float | None = None,
                      day: str | None = None, session_id: str = "", tags: str = "") -> dict:
    """Registra a mano una revisión, análisis, postura, decisión, reunión, nota o entrega.

    kind: revision | analisis | postura | decision | reunion | nota | entrega (se aceptan acentos).
    hours: horas dedicadas (opcional). day: fecha del trabajo (por defecto hoy).
    """
    con = store.connect()
    entry_id = store.add_entry(con, kind, title, body, project, hours, report.parse_day(day), session_id, tags)
    return {"id": entry_id, "ok": True}


@mcp.tool()
def worklog_entries(since: str | None = None, until: str | None = None, kind: str | None = None) -> list[dict]:
    """Lista las entradas manuales del rango."""
    start, end = _range(since, until)
    sql = "SELECT * FROM entries WHERE day >= ? AND day <= ?"
    args: list = [start.isoformat(), end.isoformat()]
    if kind:
        sql += " AND kind = ?"
        args.append(kind)
    return [dict(r) for r in store.connect().execute(sql + " ORDER BY day, id", args)]


@mcp.tool()
def worklog_delete_entry(entry_id: int) -> dict:
    """Borra una entrada manual por id."""
    con = store.connect()
    n = con.execute("DELETE FROM entries WHERE id=?", (entry_id,)).rowcount
    con.commit()
    return {"deleted": n}


@mcp.tool()
def worklog_search(query: str, since: str | None = None, limit: int = 30) -> list[dict]:
    """Busca texto en instrucciones, entregables y entradas manuales."""
    start, _ = _range(since or "-90d", None)
    con = _synced(start)
    lo, _ = store.day_bounds(start)
    like = f"%{query}%"
    hits = []
    for r in con.execute(
        "SELECT p.ts, p.session_id, p.text, s.project FROM prompts p JOIN sessions s ON s.source=p.source"
        " WHERE p.ts >= ? AND p.text LIKE ? ORDER BY p.ts DESC LIMIT ?", (lo, like, limit)):
        hits.append({"type": "prompt", "ts": store.from_iso(r["ts"]).strftime("%Y-%m-%d %H:%M"),
                     "session_id": r["session_id"], "project": r["project"], "text": r["text"][:400]})
    for r in con.execute(
        "SELECT a.ts, a.session_id, a.target, s.project FROM actions a JOIN sessions s ON s.source=a.source"
        " WHERE a.ts >= ? AND a.kind='result' AND a.target LIKE ? ORDER BY a.ts DESC LIMIT ?", (lo, like, limit)):
        hits.append({"type": "result", "ts": store.from_iso(r["ts"]).strftime("%Y-%m-%d %H:%M"),
                     "session_id": r["session_id"], "project": r["project"], "text": r["target"]})
    for r in con.execute("SELECT * FROM entries WHERE day >= ? AND (title LIKE ? OR body LIKE ?) LIMIT ?",
                         (start.isoformat(), like, like, limit)):
        hits.append({"type": f"entry:{r['kind']}", "ts": r["day"], "id": r["id"], "project": r["project"],
                     "text": f"{r['title']} — {r['body'][:300]}"})
    return sorted(hits, key=lambda h: h["ts"], reverse=True)[:limit]


def main():
    mcp.run()


if __name__ == "__main__":
    main()
