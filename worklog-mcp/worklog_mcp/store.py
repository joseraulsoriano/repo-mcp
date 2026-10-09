"""Índice SQLite de la bitácora: sesiones de Claude Code + entradas manuales."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from .ingest import parse_file

PROJECTS_DIR = Path(os.environ.get("WORKLOG_CLAUDE_PROJECTS", Path.home() / ".claude" / "projects"))
DATA_DIR = Path(os.environ.get("WORKLOG_HOME", Path.home() / ".worklog"))
# Huecos de actividad mayores a esto no cuentan como tiempo trabajado.
IDLE_MINUTES = int(os.environ.get("WORKLOG_IDLE_MINUTES", "15"))
ENTRY_KINDS = ("revision", "analisis", "postura", "decision", "reunion", "nota", "entrega")

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, mtime REAL, size INTEGER);
CREATE TABLE IF NOT EXISTS sessions (
  source TEXT PRIMARY KEY, session_id TEXT, is_subagent INTEGER, cwd TEXT, project TEXT,
  git_branch TEXT, title TEXT, kind TEXT, first_ts TEXT, last_ts TEXT,
  lines_added INTEGER, lines_removed INTEGER, cost_usd REAL, last_text TEXT);
CREATE INDEX IF NOT EXISTS sessions_sid ON sessions(session_id);
CREATE TABLE IF NOT EXISTS activity (source TEXT, ts TEXT);
CREATE INDEX IF NOT EXISTS activity_ts ON activity(ts);
CREATE TABLE IF NOT EXISTS prompts (source TEXT, session_id TEXT, ts TEXT, text TEXT);
CREATE INDEX IF NOT EXISTS prompts_ts ON prompts(ts);
CREATE TABLE IF NOT EXISTS actions (source TEXT, session_id TEXT, ts TEXT, kind TEXT, target TEXT);
CREATE INDEX IF NOT EXISTS actions_ts ON actions(ts);
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, day TEXT, kind TEXT, title TEXT,
  body TEXT, project TEXT, hours REAL, session_id TEXT, tags TEXT);
"""


def project_of(cwd: str) -> str:
    """Nombre legible del proyecto; los worktrees cuentan para su repo padre."""
    if not cwd:
        return "(sin proyecto)"
    root = cwd.split("/.claude/worktrees/")[0].split("/.claude/jobs/")[0]
    if root == str(Path.home()):
        return "~"
    return Path(root).name or root


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DATA_DIR / "worklog.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def _iso(dt: datetime) -> str:
    """Timestamps en UTC para que comparar cadenas equivalga a comparar instantes."""
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def from_iso(value: str) -> datetime:
    """Instante guardado → hora local para mostrar."""
    return datetime.fromisoformat(value).astimezone()


def sync(con: sqlite3.Connection, since: date, projects_dir: Path = PROJECTS_DIR) -> dict:
    """Indexa transcripts modificados desde `since`; sólo re-parsea los que cambiaron."""
    cutoff = datetime.combine(since, time.min).timestamp()
    seen = parsed = 0
    for path in projects_dir.rglob("*.jsonl"):
        try:
            st = path.stat()
        except OSError:
            continue
        if st.st_mtime < cutoff:
            continue
        seen += 1
        row = con.execute("SELECT mtime, size FROM files WHERE path=?", (str(path),)).fetchone()
        if row and row["mtime"] == st.st_mtime and row["size"] == st.st_size:
            continue
        s = parse_file(path)
        src = str(path)
        for table in ("sessions", "activity", "prompts", "actions"):
            con.execute(f"DELETE FROM {table} WHERE source=?", (src,))
        if s:
            con.execute(
                "INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (src, s.session_id, int(s.is_subagent), s.cwd, project_of(s.cwd), s.git_branch,
                 s.title, s.kind, _iso(min(s.activity)), _iso(max(s.activity)),
                 s.lines_added, s.lines_removed, s.cost_usd, s.last_text),
            )
            con.executemany("INSERT INTO activity VALUES (?,?)", [(src, _iso(t)) for t in s.activity])
            con.executemany("INSERT INTO prompts VALUES (?,?,?,?)",
                            [(src, s.session_id, _iso(t), p) for t, p in s.prompts])
            con.executemany("INSERT INTO actions VALUES (?,?,?,?,?)",
                            [(src, s.session_id, _iso(t), k, v) for t, k, v in s.actions])
        con.execute("INSERT OR REPLACE INTO files VALUES (?,?,?)", (src, st.st_mtime, st.st_size))
        parsed += 1
    con.commit()
    return {"transcripts_en_rango": seen, "reindexados": parsed}


# --- horas -----------------------------------------------------------------

def active_hours(stamps: list[datetime], idle_minutes: int = IDLE_MINUTES) -> float:
    """Suma los huecos entre eventos consecutivos que no superan el umbral de inactividad.

    Al aplicarse sobre la lista combinada de varias sesiones, las sesiones en paralelo
    no se cuentan dos veces.
    """
    if len(stamps) < 2:
        return 0.0
    stamps = sorted(stamps)
    limit = timedelta(minutes=idle_minutes)
    total = timedelta()
    for a, b in zip(stamps, stamps[1:]):
        gap = b - a
        if gap <= limit:
            total += gap
    return total.total_seconds() / 3600


def day_bounds(day: date) -> tuple[str, str]:
    start = datetime.combine(day, time.min).astimezone()
    return _iso(start), _iso(start + timedelta(days=1))


# --- entradas manuales -----------------------------------------------------

def add_entry(con, kind: str, title: str, body: str = "", project: str = "", hours: float | None = None,
              day: date | None = None, session_id: str = "", tags: str = "") -> int:
    kind = unicodedata.normalize("NFKD", kind.lower().strip()).encode("ascii", "ignore").decode()
    if kind not in ENTRY_KINDS:
        raise ValueError(f"kind debe ser uno de {', '.join(ENTRY_KINDS)}")
    cur = con.execute(
        "INSERT INTO entries (created_at, day, kind, title, body, project, hours, session_id, tags)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (_iso(datetime.now()), (day or date.today()).isoformat(), kind, title, body, project,
         hours, session_id, tags),
    )
    con.commit()
    return cur.lastrowid


# --- git -------------------------------------------------------------------

def git_commits(cwds: list[str], start: date, end: date) -> list[dict]:
    """Commits de todas las ramas en los repos donde hubo sesiones, sin duplicados."""
    roots: dict[str, str] = {}
    for cwd in cwds:
        if not cwd or not Path(cwd).is_dir():
            continue
        try:
            out = subprocess.run(
                ["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                capture_output=True, text=True, timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if out.returncode == 0:
            roots.setdefault(out.stdout.strip(), cwd)
    commits: dict[str, dict] = {}
    for common, cwd in roots.items():
        try:
            out = subprocess.run(
                ["git", "-C", cwd, "log", "--all", "--no-merges",
                 f"--since={start.isoformat()} 00:00", f"--until={end.isoformat()} 23:59:59",
                 "--format=%H%x1f%aI%x1f%an%x1f%s"],
                capture_output=True, text=True, timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        repo = project_of(str(Path(common).parent))
        for line in out.stdout.splitlines():
            parts = line.split("\x1f")
            if len(parts) != 4:
                continue
            sha, when, author, subject = parts
            commits.setdefault(sha, {"sha": sha, "ts": datetime.fromisoformat(when).astimezone(),
                                     "author": author, "subject": subject, "project": repo})
    return sorted(commits.values(), key=lambda c: c["ts"])
