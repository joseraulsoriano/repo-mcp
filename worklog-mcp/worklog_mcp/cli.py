"""CLI: `worklog report --since lunes --detail completo --out ~/.worklog/semana.md`."""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path

from . import jira, publish, report, store


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="worklog", description="Bitácora de trabajo desde Claude Code + git")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("report", help="genera la bitácora en Markdown")
    r.add_argument("--since", default=None, help="YYYY-MM-DD, lunes, ayer, -7d (por defecto: lunes)")
    r.add_argument("--until", default=None, help="por defecto: hoy")
    r.add_argument("--project", default=None)
    r.add_argument("--detail", default="breve", choices=["breve", "completo"])
    r.add_argument("--out", default=None, help="archivo .md de salida (si no, stdout)")

    s = sub.add_parser("sync", help="reindexa transcripts")
    s.add_argument("--since", default=None)

    e = sub.add_parser("add", help="registra una entrada manual")
    e.add_argument("kind", choices=store.ENTRY_KINDS)
    e.add_argument("title")
    e.add_argument("--body", default="")
    e.add_argument("--project", default="")
    e.add_argument("--hours", type=float, default=None)
    e.add_argument("--day", default=None)

    pb = sub.add_parser("publish", help="manda los días al panel de RTC Soluciones (/admin/bitacora)")
    pb.add_argument("--since", default="-6d", help="por defecto: -6d (los últimos 7 días)")
    pb.add_argument("--until", default=None, help="por defecto: hoy")

    j = sub.add_parser("jira", help="avisa a Jira del trabajo hecho (sólo tareas asignadas a ti)")
    j.add_argument("--since", default="ayer", help="por defecto: ayer")
    j.add_argument("--until", default=None, help="por defecto: hoy")
    j.add_argument("--dry-run", action="store_true", help="muestra lo que haría sin tocar Jira")
    j.add_argument("--close", default=None, metavar="CLAVE", help="marca esa tarea como terminada")
    j.add_argument("--note", default="", help="comentario al cerrar")
    j.add_argument("--configure", action="store_true",
                   help="pide URL, correo y token, los prueba y los guarda (token en el Llavero)")

    sub.add_parser("snapshot", help="para hooks: escribe hoy.md, semana.md y semanas/<lunes>.md; nunca falla")

    args = ap.parse_args(argv)
    if args.cmd == "snapshot":
        snapshot()
        return
    con = store.connect()
    if args.cmd == "sync":
        print(store.sync(con, report.parse_day(args.since, report.this_monday())))
    elif args.cmd == "jira":
        out = (jira.configure() if args.configure else jira.close(args.close, args.note) if args.close else
               jira.sync(con, report.parse_day(args.since), report.parse_day(args.until), args.dry_run))
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.cmd == "publish":
        print(publish.publish(con, report.parse_day(args.since), report.parse_day(args.until)))
    elif args.cmd == "add":
        print(store.add_entry(con, args.kind, args.title, args.body, args.project, args.hours,
                              report.parse_day(args.day)))
    else:
        start = report.parse_day(args.since, report.this_monday())
        end = report.parse_day(args.until)
        store.sync(con, start)
        md = report.render(report.collect(con, start, end, args.project), args.detail)
        if args.out:
            path = Path(args.out).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(md, encoding="utf-8")
            print(f"Bitácora guardada en {path}")
        else:
            print(md)


def snapshot(home: Path | None = None) -> None:
    """Pensado para el hook SessionEnd: silencioso y sin romper el cierre de sesión."""
    home = home or store.DATA_DIR
    try:
        con = store.connect(home / "worklog.db")
        monday, today = report.this_monday(), report.parse_day("hoy")
        store.sync(con, monday)
        week = report.render(report.collect(con, monday, today), "breve")
        files = {
            home / "hoy.md": report.render(report.collect(con, today, today), "completo"),
            home / "semana.md": week,
            home / "semanas" / f"{monday.isoformat()}.md": week,
        }
        for path, md in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(md, encoding="utf-8")
        # Ayer también: una sesión que cruzó la medianoche cambia los dos días.
        if publish.config(home):
            publish.publish(con, today - timedelta(days=1), today, timeout=10, home=home)
        if jira.config(home):
            out = jira.sync(con, today - timedelta(days=1), today, home=home, timeout=5)
            (home / "jira.md").write_text(_jira_md(out), encoding="utf-8")
    except Exception:
        home.mkdir(parents=True, exist_ok=True)
        with (home / "hook.log").open("a", encoding="utf-8") as log:
            log.write(f"--- {datetime.now().isoformat(timespec='seconds')}\n{traceback.format_exc()}")


def _jira_md(out: dict) -> str:
    """Resumen legible de la última sincronización con Jira (`~/.worklog/jira.md`)."""
    lines = [f"# Jira · {out['desde']} → {out['hasta']}", "", "## Vinculadas"]
    lines += [f"- {v['clave']} {v['tarea']} · {v['dia']} · {v.get('horas', 0)} h · {v['estado']}"
              for v in out["vinculadas"]] or ["- (ninguna)"]
    lines += ["", "## Omitidas (regla «sólo sí»)"]
    lines += [f"- {o['clave']}: {o['motivo']}" for o in out["omitidas"]] or ["- (ninguna)"]
    lines += ["", f"## Sin tarea en Jira · {out['sin_tarea_horas']} h"]
    lines += [f"- {u['dia']} · {u['proyecto']} · {u['titulo']} · {u['horas']} h"
              for u in out["sin_tarea"]] or ["- (ninguna)"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
