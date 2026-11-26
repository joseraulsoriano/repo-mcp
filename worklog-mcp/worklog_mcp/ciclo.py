"""Cuánto tardamos: publicaciones (tags), fecha de pedido de cada ticket y bugs, en todos los repos.

La bitácora ya trae los commits de cada día. Para medir un cambio de punta a punta faltaban tres
cosas, y las tres salen de aquí:

- **Cuándo se publicó.** Un tag de publicación (`v2026.11.25.4`, `cliente/v…`) y los commits que
  trae de nuevo respecto al tag anterior del mismo repo (`git log anterior..tag`). Viajan en el día
  del tag, con la lista de shas: así un commit de hace una semana sabe en qué publicación salió
  aunque su día no se vuelva a mandar.
- **Cuándo se pidió.** La fecha de creación del ticket en Jira (`KAN-139`), guardada en `tickets`
  para no preguntarla en cada `publish`. Un ticket de otro sitio de Jira (404) se queda sin fecha y
  el panel usa el primer commit.
- **Bugs.** Se anotan al encontrarlos (`worklog_bug`) y se cierran solos cuando llega un commit
  `fix(...)` del mismo proyecto que menciona su ticket o `BUG-<id>`. Viajan en el día en que se
  abrieron y en el día en que se cerraron; el panel los junta por id.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TAG_PUBLICACION = re.compile(r"(^|/)v\d{4}\.\d{2}\.\d{2}(\.\d+)?$")
BUG_REF = re.compile(r"\bBUG-(\d+)\b", re.IGNORECASE)
ES_FIX = re.compile(r"^(fix|hotfix|revert)\b", re.IGNORECASE)
MAX_SHAS = 400
# Un ticket sin fecha (404, sin config) se vuelve a preguntar pasado este tiempo.
REINTENTO = timedelta(days=1)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (clave TEXT PRIMARY KEY, creado TEXT, consultado TEXT, epica INTEGER DEFAULT 0, sitio TEXT);
CREATE TABLE IF NOT EXISTS bugs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, abierto TEXT, proyecto TEXT, ticket TEXT, titulo TEXT,
  cuerpo TEXT, cerrado TEXT, fix_sha TEXT);
"""


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def asegurar(con) -> None:
    con.executescript(SCHEMA)
    columnas = {f[1] for f in con.execute("PRAGMA table_info(tickets)")}
    # La primera versión no sabía de qué sitio era la fecha: se descarta y se vuelve a preguntar.
    if "sitio" not in columnas:
        con.execute("DROP TABLE tickets")
        con.executescript(SCHEMA)


# --- publicaciones -----------------------------------------------------------------------------

def _git(cwd: str, *args: str, timeout: int = 20) -> str:
    try:
        out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout if out.returncode == 0 else ""


def publicaciones(roots: dict[str, str], start: date, end: date, project_of) -> list[dict]:
    """Tags de publicación creados en [start, end] en cada repo, con los commits que estrenan."""
    desde = datetime.combine(start, datetime.min.time()).astimezone()
    hasta = datetime.combine(end, datetime.max.time()).astimezone()
    salida = []
    for common, cwd in roots.items():
        filas = _git(cwd, "for-each-ref", "refs/tags", "--sort=creatordate",
                     "--format=%(refname:short)%1f%(creatordate:iso-strict)")
        tags = []
        for linea in filas.splitlines():
            partes = linea.split("\x1f")
            if len(partes) == 2 and TAG_PUBLICACION.search(partes[0]):
                try:
                    tags.append((partes[0], datetime.fromisoformat(partes[1]).astimezone()))
                except ValueError:
                    continue
        proyecto = project_of(str(Path(common).parent))
        # El anterior es el del mismo prefijo (sitio y clientes llevan su propia serie de tags).
        anterior: dict[str, str] = {}
        for nombre, ts in tags:
            prefijo = nombre.rsplit("/", 1)[0] if "/" in nombre else ""
            previo = anterior.get(prefijo)
            anterior[prefijo] = nombre
            if not (desde <= ts <= hasta):
                continue
            rango = f"{previo}..{nombre}" if previo else nombre
            shas = _git(cwd, "log", "--no-merges", "--format=%H", f"--max-count={MAX_SHAS}", rango).split()
            salida.append({"proyecto": proyecto, "tag": nombre, "ts": ts, "shas": shas})
    return sorted(salida, key=lambda p: p["ts"])


# --- tickets ------------------------------------------------------------------------------------

def fechas_tickets(con, claves: set[str], sitios: list | None = None,
                   ahora: datetime | None = None) -> dict[str, dict]:
    """{clave: {creado, epica}} de los tickets que se conocen. Pregunta a Jira sólo lo que falta.

    `sitios` es [(prefijos, cliente)] (jira.sitios): cada clave va sólo al sitio de su prefijo; una
    clave sin sitio no se pregunta (no se adivina con otro Jira).
    """
    asegurar(con)
    ahora = ahora or datetime.now(timezone.utc)
    sitios = sitios or []
    conocidas: dict[str, dict] = {}
    for clave in sorted(claves):
        fila = con.execute("SELECT creado, consultado, epica FROM tickets WHERE clave=?", (clave,)).fetchone()
        if fila and fila["creado"]:
            conocidas[clave] = {"creado": fila["creado"], "epica": bool(fila["epica"])}
            continue
        if fila and fila["consultado"] and datetime.fromisoformat(fila["consultado"]) >= ahora - REINTENTO:
            continue
        jira = next((c for prefijos, c in sitios if clave.split("-")[0] in prefijos), None)
        if jira is None:
            continue
        ficha = None
        try:
            ficha = jira.ficha(clave)
        except RuntimeError:
            pass  # sin red o sin permiso: se reintenta otro día, nunca tumba el publish
        con.execute("INSERT INTO tickets (clave, creado, consultado, epica, sitio) VALUES (?,?,?,?,?) "
                    "ON CONFLICT(clave) DO UPDATE SET creado=excluded.creado, consultado=excluded.consultado, "
                    "epica=excluded.epica, sitio=excluded.sitio",
                    (clave, ficha and ficha["creado"], _iso(ahora), int(bool(ficha and ficha["epica"])),
                     getattr(jira, "url", "")))
        if ficha:
            conocidas[clave] = ficha
    con.commit()
    return conocidas


# --- bugs ---------------------------------------------------------------------------------------

def abrir_bug(con, titulo: str, proyecto: str, ticket: str = "", cuerpo: str = "",
              cuando: datetime | None = None) -> int:
    asegurar(con)
    titulo, proyecto = titulo.strip(), proyecto.strip()
    if not titulo or not proyecto:
        raise ValueError("Un bug necesita título y proyecto (el nombre del repo, p. ej. rtcsolutions-web).")
    cur = con.execute("INSERT INTO bugs (abierto, proyecto, ticket, titulo, cuerpo) VALUES (?,?,?,?,?)",
                      (_iso(cuando or datetime.now()), proyecto, ticket.strip().upper(), titulo, cuerpo))
    con.commit()
    return cur.lastrowid


def cerrar_bugs(con, commits: list[dict]) -> list[int]:
    """Cierra los bugs abiertos que un commit `fix(...)` del mismo proyecto resuelve. Idempotente."""
    asegurar(con)
    cerrados = []
    abiertos = con.execute("SELECT * FROM bugs WHERE cerrado IS NULL").fetchall()
    for bug in abiertos:
        abierto = datetime.fromisoformat(bug["abierto"])
        for c in sorted(commits, key=lambda c: c["ts"]):
            asunto = c["subject"]
            if c["project"].lower() != (bug["proyecto"] or "").lower() or c["ts"] < abierto:
                continue
            if not ES_FIX.search(asunto):
                continue
            por_id = any(int(m) == bug["id"] for m in BUG_REF.findall(asunto))
            por_ticket = bool(bug["ticket"]) and re.search(rf"\b{re.escape(bug['ticket'])}\b", asunto)
            if por_id or por_ticket:
                con.execute("UPDATE bugs SET cerrado=?, fix_sha=? WHERE id=? AND cerrado IS NULL",
                            (_iso(c["ts"]), c["sha"], bug["id"]))
                cerrados.append(bug["id"])
                break
    con.commit()
    return cerrados


def bugs_del_dia(con, dia: date) -> list[dict]:
    """Los bugs que se abrieron o cerraron ese día (hora local), para el envío al panel."""
    asegurar(con)
    inicio = datetime.combine(dia, datetime.min.time()).astimezone()
    fin = inicio + timedelta(days=1)
    lim = (_iso(inicio), _iso(fin))
    filas = con.execute("SELECT * FROM bugs WHERE (abierto >= ? AND abierto < ?) OR (cerrado >= ? AND cerrado < ?) "
                        "ORDER BY id", (*lim, *lim)).fetchall()
    return [{"id": f["id"], "proyecto": f["proyecto"], "ticket": f["ticket"] or "", "titulo": f["titulo"],
             "abierto": f["abierto"], "cerrado": f["cerrado"] or "", "fix": f["fix_sha"] or ""} for f in filas]


def listar_bugs(con, estado: str = "abiertos") -> list[dict]:
    asegurar(con)
    donde = {"abiertos": "cerrado IS NULL", "cerrados": "cerrado IS NOT NULL"}.get(estado, "1=1")
    return [dict(f) for f in con.execute(f"SELECT * FROM bugs WHERE {donde} ORDER BY id DESC LIMIT 200")]
