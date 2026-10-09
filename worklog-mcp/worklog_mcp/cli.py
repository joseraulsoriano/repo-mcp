"""CLI: `worklog report --since lunes --detail completo --out ~/.worklog/semana.md`."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import report, store


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

    args = ap.parse_args(argv)
    con = store.connect()
    if args.cmd == "sync":
        print(store.sync(con, report.parse_day(args.since, report.this_monday())))
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


if __name__ == "__main__":
    main()
