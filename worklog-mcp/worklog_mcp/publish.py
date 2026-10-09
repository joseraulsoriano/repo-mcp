"""Publica la bitácora en el panel de RTC Soluciones (`/admin/bitacora`).

La base vive en esta máquina y el panel corre en Cloudflare, así que aquí se arma un resumen por
día y se empuja a `POST {url}/api/bitacora/dias` con `Authorization: Bearer {token}`.

Configuración (lo primero que exista gana):
- `WORKLOG_PANEL_URL` y `WORKLOG_PANEL_TOKEN` en el entorno.
- `~/.worklog/panel.json` con `{"url": "...", "token": "..."}`. Lo usa el hook `SessionEnd`,
  que no siempre hereda el entorno de la terminal.

Qué no sale de la máquina: los comandos de shell (pueden llevar secretos) y las instrucciones
completas; de cada sesión viaja sólo la primera, recortada.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from . import report, store

ENDPOINT = "/api/bitacora/dias"
# Días por petición: cada uno pesa pocos KB, 30 dejan el cuerpo muy por debajo del límite.
LOTE = 30


def config(home: Path | None = None) -> tuple[str, str] | None:
    """(url, token) o None si la publicación no está configurada."""
    url = os.environ.get("WORKLOG_PANEL_URL", "").strip()
    token = os.environ.get("WORKLOG_PANEL_TOKEN", "").strip()
    if not (url and token):
        path = (home or store.DATA_DIR) / "panel.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        url = url or str(data.get("url", "")).strip()
        token = token or str(data.get("token", "")).strip()
    return (url.rstrip("/"), token) if url and token else None


def _iso(dt) -> str:
    return store._iso(dt) if dt else ""


def build_days(data: dict) -> list[dict]:
    """`report.collect` → el contrato de `src/lib/bitacora.ts` (DiaBitacora)."""
    days = []
    for day in data["days"]:
        projects = []
        for name, p in day["projects"].items():
            sessions = []
            for s in p["sessions"]:
                sessions.append({
                    "id": s["session_id"],
                    "titulo": report._short(s["title"], 200),
                    "rama": s["branch"] or "",
                    "tipo": s["kind"] or "",
                    "inicio": _iso(s["start"]),
                    "fin": _iso(s["end"]),
                    "horas": round(s["hours"], 4),
                    "instrucciones": len(s["prompts"]),
                    "primera": report._short(s["prompts"][0][1], 300) if s["prompts"] else "",
                    "resultados": [report._short(r, 400) for r in s["results"][-5:]],
                    "skills": [report._short(x, 80) for x in s["skills"][:12]],
                    "archivos": [report._rel(f, s["cwd"]) for f in s["files"][:60]],
                    "subagentes": len(s["agents"]),
                    "lineas_mas": s["lines_added"],
                    "lineas_menos": s["lines_removed"],
                    "costo": round(s["cost"], 4),
                    "worktree": "/.claude/worktrees/" in (s["cwd"] or ""),
                })
            projects.append({"nombre": name, "horas": round(p["hours"], 4), "sesiones": sessions})
        days.append({
            "dia": day["day"].isoformat(),
            "horas": round(day["hours"], 4),
            "proyectos": projects,
            "commits": [{"sha": c["sha"], "ts": _iso(c["ts"]), "proyecto": c["project"],
                         "asunto": report._short(c["subject"], 300)} for c in day["commits"]],
            "entradas": [{"tipo": e["kind"], "titulo": e["title"], "cuerpo": e["body"] or "",
                          "proyecto": e["project"] or "", "horas": e["hours"]} for e in day["entries"]],
        })
    return days


def _post(url: str, token: str, body: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        url + ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                 "User-Agent": "worklog-mcp"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read() or b"{}")
    except urllib.error.HTTPError as err:
        try:
            detail = json.loads(err.read() or b"{}")
        except ValueError:
            detail = {}
        problems = "; ".join(detail.get("problemas", [])[:5])
        raise RuntimeError(f"El panel respondió {err.code}: {detail.get('error', err.reason)}"
                           + (f" ({problems})" if problems else "")) from None


def publish(con, start: date, end: date, timeout: float = 20.0, home: Path | None = None) -> dict:
    """Sincroniza, arma los días [start, end] y los manda. Lanza si falta configuración o el panel falla."""
    cfg = config(home)
    if not cfg:
        raise RuntimeError("Falta configurar el panel: WORKLOG_PANEL_URL y WORKLOG_PANEL_TOKEN, "
                           "o ~/.worklog/panel.json con url y token.")
    url, token = cfg
    store.sync(con, start)
    days = build_days(report.collect(con, start, end))
    sent = 0
    for i in range(0, len(days), LOTE):
        _post(url, token, {"origen": "worklog-mcp", "dias": days[i:i + LOTE]}, timeout)
        sent += len(days[i:i + LOTE])
    return {"panel": url, "dias": sent, "desde": start.isoformat(), "hasta": end.isoformat()}
