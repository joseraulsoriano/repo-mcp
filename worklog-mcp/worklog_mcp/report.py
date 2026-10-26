"""Bitácora en Markdown: día → proyecto → sesión, más commits y entradas manuales."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from . import store

DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
WEEKDAYS = {"lunes": 0, "monday": 0, "martes": 1, "tuesday": 1, "miercoles": 2, "miércoles": 2,
            "wednesday": 2, "jueves": 3, "thursday": 3, "viernes": 4, "friday": 4,
            "sabado": 5, "sábado": 5, "saturday": 5, "domingo": 6, "sunday": 6}


def parse_day(value: str | None, default: date | None = None) -> date:
    """Acepta YYYY-MM-DD, hoy/today, ayer/yesterday, un día de la semana (el de esta semana) o -Nd."""
    today = date.today()
    if not value:
        return default or today
    v = value.strip().lower()
    if v in ("hoy", "today"):
        return today
    if v in ("ayer", "yesterday"):
        return today - timedelta(days=1)
    if v in WEEKDAYS:
        return today - timedelta(days=(today.weekday() - WEEKDAYS[v]) % 7)
    m = re.fullmatch(r"-(\d+)d", v)
    if m:
        return today - timedelta(days=int(m.group(1)))
    return date.fromisoformat(v)


def this_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def fmt_day(d: date) -> str:
    return f"{DAYS_ES[d.weekday()]} {d.day} {MONTHS_ES[d.month - 1]}"


def fmt_h(hours: float) -> str:
    h, m = divmod(round(hours * 60), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def _short(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


SCRATCH = re.compile(r"/\.claude/jobs/[^/]+/tmp/|^/tmp/|^/private/tmp/|^/var/folders/")
WORKTREE_PREFIX = re.compile(r"^\.claude/worktrees/[^/]+/")


def _is_deliverable(path: str) -> bool:
    return not SCRATCH.search(path)


def _rel(path: str, cwd: str) -> str:
    root = cwd.split("/.claude/worktrees/")[0]
    for base in (cwd, root):
        if base and path.startswith(base + "/"):
            return WORKTREE_PREFIX.sub("", path[len(base) + 1:])
    return path.replace(str(Path.home()), "~")


def collect(con, start: date, end: date, project: str | None = None) -> dict:
    """Agrupa la actividad del rango [start, end] (ambos incluidos)."""
    lo, _ = store.day_bounds(start)
    _, hi = store.day_bounds(end)
    meta = {}
    for r in con.execute("SELECT * FROM sessions WHERE last_ts >= ? AND first_ts < ?", (lo, hi)):
        if project and r["project"].lower() != project.lower():
            continue
        m = meta.setdefault(r["session_id"], {"session_id": r["session_id"], "project": r["project"],
                                              "cwd": r["cwd"], "title": "", "branch": "", "kind": "",
                                              "lines_added": 0, "lines_removed": 0, "cost": 0.0,
                                              "last_text": ""})
        if not r["is_subagent"]:
            m.update(project=r["project"], cwd=r["cwd"], title=r["title"] or m["title"],
                     branch=r["git_branch"] or m["branch"], kind=r["kind"], last_text=r["last_text"])
        m["lines_added"] += r["lines_added"] or 0
        m["lines_removed"] += r["lines_removed"] or 0
        m["cost"] += r["cost_usd"] or 0
    days = []
    totals_sessions, totals_prompts, totals_files = set(), 0, set()
    d = start
    while d <= end:
        dlo, dhi = store.day_bounds(d)
        stamps = defaultdict(list)  # session_id -> instantes (sesión + sus subagentes)
        for r in con.execute(
            "SELECT s.session_id, a.ts FROM activity a JOIN sessions s ON s.source=a.source"
            " WHERE a.ts >= ? AND a.ts < ?", (dlo, dhi)):
            if r["session_id"] in meta:
                stamps[r["session_id"]].append(store.from_iso(r["ts"]))
        prompts, actions = defaultdict(list), defaultdict(list)
        for r in con.execute("SELECT session_id, ts, text FROM prompts WHERE ts >= ? AND ts < ? ORDER BY ts",
                             (dlo, dhi)):
            if r["session_id"] in meta:
                prompts[r["session_id"]].append((store.from_iso(r["ts"]), r["text"]))
        for r in con.execute("SELECT session_id, ts, kind, target FROM actions WHERE ts >= ? AND ts < ? ORDER BY ts",
                             (dlo, dhi)):
            if r["session_id"] in meta:
                actions[r["session_id"]].append((r["kind"], r["target"]))
        by_project = defaultdict(lambda: {"stamps": [], "sessions": []})
        for sid, st in stamps.items():
            if not prompts[sid] and not actions[sid]:
                continue  # sesiones vacías (/clear, aperturas sin trabajo)
            m = meta[sid]
            files = sorted({t for k, t in actions[sid] if k == "edit" and _is_deliverable(t)})
            sess = {**m, "start": min(st), "end": max(st), "hours": store.active_hours(st),
                    "prompts": prompts[sid], "files": files,
                    "results": [t for k, t in actions[sid] if k == "result"],
                    "skills": sorted({t for k, t in actions[sid] if k in ("skill", "review")}),
                    "shell": [t for k, t in actions[sid] if k == "shell"],
                    "agents": [t for k, t in actions[sid] if k == "agent"]}
            if not sess["title"]:
                sess["title"] = _short(prompts[sid][0][1], 80) if prompts[sid] else "(sin título)"
            p = by_project[m["project"]]
            p["stamps"].extend(st)
            p["sessions"].append(sess)
            totals_sessions.add(sid)
            totals_prompts += len(prompts[sid])
            totals_files.update(files)
        all_stamps = [t for p in by_project.values() for t in p["stamps"]]
        projects = {name: {"hours": store.active_hours(p["stamps"]),
                           "sessions": sorted(p["sessions"], key=lambda s: s["start"])}
                    for name, p in by_project.items()}
        entries = [dict(r) for r in con.execute("SELECT * FROM entries WHERE day=? ORDER BY id", (d.isoformat(),))
                   if not project or (r["project"] or "").lower() == project.lower()]
        days.append({"day": d, "hours": store.active_hours(all_stamps), "projects": projects,
                     "entries": entries, "commits": []})
        d += timedelta(days=1)

    commits = store.git_commits(sorted({m["cwd"] for m in meta.values()}), start, end)
    if project:
        commits = [c for c in commits if c["project"].lower() == project.lower()]
    for c in commits:
        idx = (c["ts"].date() - start).days
        if 0 <= idx < len(days):
            days[idx]["commits"].append(c)

    worked = [m for sid, m in meta.items() if sid in totals_sessions]
    return {
        "start": start, "end": end, "project": project, "days": days,
        "totals": {
            "hours": sum(x["hours"] for x in days),
            "manual_hours": sum((e["hours"] or 0) for x in days for e in x["entries"]),
            "sessions": len(totals_sessions),
            "prompts": totals_prompts,
            "files": len(totals_files),
            "commits": len(commits),
            "lines_added": sum(m["lines_added"] for m in worked),
            "lines_removed": sum(m["lines_removed"] for m in worked),
            "cost": sum(m["cost"] for m in worked),
            "entries": sum(len(x["entries"]) for x in days),
        },
    }


def render(data: dict, detail: str = "breve") -> str:
    full = detail.startswith(("comp", "full"))
    t = data["totals"]
    scope = f" · proyecto `{data['project']}`" if data["project"] else ""
    out = [f"# Bitácora de trabajo — {fmt_day(data['start'])} → {fmt_day(data['end'])} {data['end'].year}{scope}",
           "",
           f"**{fmt_h(t['hours'])} activas** en Claude Code"
           + (f" + {fmt_h(t['manual_hours'])} registradas a mano" if t["manual_hours"] else "")
           + f" · {t['sessions']} sesiones · {t['prompts']} instrucciones · {t['files']} archivos editados"
           f" · {t['commits']} commits · +{t['lines_added']}/−{t['lines_removed']} líneas"
           + (f" · {t['entries']} entradas (revisiones/análisis/posturas)" if t["entries"] else ""),
           ""]

    proj_tot = defaultdict(lambda: {"hours": 0.0, "sessions": 0, "commits": 0})
    for day in data["days"]:
        for name, p in day["projects"].items():
            proj_tot[name]["hours"] += p["hours"]
            proj_tot[name]["sessions"] += len(p["sessions"])
        for c in day["commits"]:
            proj_tot[c["project"]]["commits"] += 1
    if proj_tot:
        out += ["## Por proyecto", "", "| Proyecto | Horas | Sesiones | Commits |", "|---|---:|---:|---:|"]
        for name, p in sorted(proj_tot.items(), key=lambda kv: -kv[1]["hours"]):
            out.append(f"| {name} | {fmt_h(p['hours'])} | {p['sessions']} | {p['commits']} |")
        out.append("")

    for day in data["days"]:
        if not day["projects"] and not day["entries"] and not day["commits"]:
            continue
        out += [f"## {fmt_day(day['day'])} — {fmt_h(day['hours'])}", ""]
        commits_by_proj = defaultdict(list)
        for c in day["commits"]:
            commits_by_proj[c["project"]].append(c)
        for name in sorted(set(day["projects"]) | set(commits_by_proj),
                           key=lambda n: -day["projects"].get(n, {"hours": 0})["hours"]):
            p = day["projects"].get(name, {"hours": 0.0, "sessions": []})
            out.append(f"### {name} · {fmt_h(p['hours'])}")
            for s in p["sessions"]:
                tag = " · bg" if s["kind"] == "bg" else ""
                out.append(f"- **{_short(s['title'], 90)}** · {s['start']:%H:%M}–{s['end']:%H:%M}"
                           f" · {fmt_h(s['hours'])} · {len(s['prompts'])} instr. · {len(s['files'])} archivos{tag}")
                for r in s["results"][-2:]:
                    out.append(f"  - ✅ {_short(r, 220)}")
                if s["skills"]:
                    out.append(f"  - 🔎 {', '.join(_short(x, 60) for x in s['skills'][:6])}")
                if full:
                    if s["branch"]:
                        out.append(f"  - rama `{s['branch']}` · sesión `{s['session_id'][:8]}`")
                    for ts, text in s["prompts"][:8]:
                        out.append(f"  - {ts:%H:%M} › {_short(text, 200)}")
                    if len(s["prompts"]) > 8:
                        out.append(f"  - … {len(s['prompts']) - 8} instrucciones más")
                    if s["files"]:
                        shown = [f"`{_rel(f, s['cwd'])}`" for f in s["files"][:12]]
                        more = f" (+{len(s['files']) - 12})" if len(s["files"]) > 12 else ""
                        out.append(f"  - archivos: {', '.join(shown)}{more}")
                    for cmd in s["shell"][:5]:
                        out.append(f"  - `$ {_short(cmd, 140)}`")
                    if s["agents"]:
                        out.append(f"  - subagentes: {', '.join(_short(a, 50) for a in s['agents'][:5])}")
                    if not s["results"] and s["last_text"]:
                        out.append(f"  - último mensaje: {_short(s['last_text'], 220)}")
                elif s["prompts"] and not s["results"]:
                    out.append(f"  - › {_short(s['prompts'][0][1], 160)}")
            for c in commits_by_proj.get(name, []):
                who = f" ({c['author']})" if full else ""
                out.append(f"- `{c['sha'][:7]}` {c['ts']:%H:%M} {_short(c['subject'], 120)}{who}")
            out.append("")
        if day["entries"]:
            out.append("### Registro manual")
            for e in day["entries"]:
                extra = ", ".join(x for x in [fmt_h(e["hours"]) if e["hours"] else "", e["project"] or ""] if x)
                line = f"- **[{e['kind']}]** {e['title']}" + (f" ({extra})" if extra else "")
                if e["body"]:
                    line += f" — {_short(e['body'], 400 if full else 160)}"
                out.append(line)
            out.append("")

    out += ["---",
            f"_Horas activas = suma de intervalos entre eventos de la sesión separados por ≤ {store.IDLE_MINUTES} min,"
            " sin contar dos veces sesiones en paralelo. Incluye el tiempo en que el agente trabajó"
            " (sesiones `bg`). Fuente: `~/.claude/projects` (y los perfiles `~/.claude-*`) + `git log --all` de cada repo._"]
    return "\n".join(out)
