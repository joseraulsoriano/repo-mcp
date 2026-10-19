"""Avisa a Jira de lo que trabajaste, sólo en tareas que existen y están asignadas a ti.

Regla «sólo sí»: una sesión se vincula a una tarea únicamente si su clave (`QYCA-15`) aparece donde
hay intención de trabajarla —la rama, un commit hecho en la sesión o su primera instrucción— y
Jira confirma que la tarea existe y su responsable eres tú. Una mención de pasada en otra
instrucción no cuenta, y el trabajo sin tarea (la web de otro sistema, por ejemplo) no se vincula a
nada: sale en `sin_tarea` para que se vea qué no quedó en Jira.

Qué hace con cada tarea vinculada:
- «Por hacer» → «En curso» al detectar trabajo. Nunca reabre una tarea terminada.
- → «Listo» sólo con una señal explícita en una instrucción o un commit: «cierra QYCA-15»,
  «closes QYCA-15», «QYCA-15 listo».
- Un comentario por sesión con fecha, horas, entregables y archivos; si la sesión sigue, el mismo
  comentario se actualiza en lugar de duplicarse.

Qué sale de la máquina: el título de la sesión, sus entregables (`result:`), número de archivos y
asuntos de commit. Nunca los comandos de shell ni las instrucciones completas.

Configuración (como el panel): `WORKLOG_JIRA_URL`, `WORKLOG_JIRA_EMAIL` y `WORKLOG_JIRA_TOKEN`, o
`~/.worklog/jira.json` con `{"url": ..., "email": ...}` y el token en el Llavero de macOS
(`worklog jira --configure`, que lo prueba antes de guardarlo). El token es un API token de
https://id.atlassian.com/manage-profile/security/api-tokens.
"""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from . import publish, report, store

KEYCHAIN_SERVICE = "worklog-jira"
KEY = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d+)\b")
_KEYS = r"[A-Z][A-Z0-9]{1,9}-\d+(?:\s*(?:,|y|and|&)\s*[A-Z][A-Z0-9]{1,9}-\d+)*"
CLOSE = re.compile(
    rf"\b(?:cierra|cerrar|cerré|closes?|closed|fix(?:es|ed)?|resuelve|resolves?|termin[eéa])\s*:?\s*({_KEYS})"
    rf"|({_KEYS})\s*(?:listo|lista|terminad[ao]|done|cerrad[ao])\b",
    re.IGNORECASE,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jira_comments (
  session_id TEXT, issue TEXT, comment_id TEXT, PRIMARY KEY (session_id, issue));
"""


def site(url: str) -> str:
    """Cualquier URL del sitio (`…/jira/for-you?tab=assigned`) → `https://sitio.atlassian.net`."""
    url = url.strip()
    if url and "://" not in url:
        url = "https://" + url
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}" if parts.netloc else ""


def config(home: Path | None = None) -> tuple[str, str, str] | None:
    """(url, email, token) o None si Jira no está configurado."""
    url = os.environ.get("WORKLOG_JIRA_URL", "").strip()
    email = os.environ.get("WORKLOG_JIRA_EMAIL", "").strip()
    token = os.environ.get("WORKLOG_JIRA_TOKEN", "").strip() or publish.keychain_token(KEYCHAIN_SERVICE)
    if not (url and email and token):
        try:
            data = json.loads(((home or store.DATA_DIR) / "jira.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        url = url or str(data.get("url", "")).strip()
        email = email or str(data.get("email", "")).strip()
        token = token or str(data.get("token", "")).strip()
    return (site(url), email, token) if url and email and token else None


def configure(home: Path | None = None, prompt=input, secret=None, save_token=None) -> dict:
    """Pide URL, correo y token; los prueba contra Jira y sólo si funcionan los guarda.

    El token va al Llavero con `security -w <token>` y no por su aviso interactivo, que recorta lo
    que se escribe a 128 caracteres: los API tokens de Atlassian son más largos.
    """
    import getpass

    home = home or store.DATA_DIR
    path = home / "jira.json"
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        saved = {}
    url = site(prompt(f"URL de Jira [{saved.get('url', '')}]: ").strip() or saved.get("url", ""))
    email = prompt(f"Correo de tu cuenta Atlassian [{saved.get('email', '')}]: ").strip() or saved.get("email", "")
    token = (secret or getpass.getpass)("API token (no se muestra): ").strip()
    if not (url and email and token):
        raise RuntimeError("Faltan datos: URL, correo y token son obligatorios.")
    me = Jira(url, email, token)._call("GET", "/rest/api/3/myself")
    (save_token or _keychain_save)(token)
    home.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"url": url, "email": email}, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return {"ok": True, "cuenta": me.get("displayName", ""), "url": url,
            "token_caracteres": len(token)}


def _keychain_save(token: str) -> None:
    import subprocess

    out = subprocess.run(["security", "add-generic-password", "-U", "-s", KEYCHAIN_SERVICE,
                          "-a", os.environ.get("USER", "worklog"), "-w", token],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        raise RuntimeError(f"No se pudo guardar el token en el Llavero: {out.stderr.strip()}")


def keys_in(text: str) -> set[str]:
    return set(KEY.findall(text or ""))


def closed_in(text: str) -> set[str]:
    out: set[str] = set()
    for m in CLOSE.finditer(text or ""):
        out |= keys_in(m.group(1) or m.group(2))
    return out


def _commit_messages(shell: list[str]) -> list[str]:
    return [c for c in shell if re.search(r"\bgit\s+commit\b", c)]


def evidence(sess: dict) -> tuple[set[str], set[str]]:
    """(claves trabajadas, claves cerradas) de una sesión de `report.collect`."""
    first = sess["prompts"][0][1] if sess["prompts"] else ""
    commits = _commit_messages(sess["shell"])
    worked = keys_in(sess["branch"]) | keys_in(first) | set().union(*map(keys_in, commits), set())
    closed = set().union(*(closed_in(t) for _, t in sess["prompts"]), set()) | set().union(
        *map(closed_in, commits), set())
    return worked | closed, closed


class Jira:
    """Cliente mínimo de la API REST v3 de Jira Cloud."""

    def __init__(self, url: str, email: str, token: str, timeout: float = 15.0):
        self.url, self.timeout = url, timeout
        self.auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()

    def _call(self, method: str, path: str, body: dict | None = None):
        req = urllib.request.Request(
            self.url + path, method=method,
            data=json.dumps(body).encode("utf-8") if body is not None else None,
            headers={"Authorization": self.auth, "Accept": "application/json",
                     "Content-Type": "application/json", "User-Agent": "worklog-mcp"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read()
                try:
                    return json.loads(raw) if raw else {}
                except ValueError:
                    raise RuntimeError(f"{self.url} no respondió como la API de Jira (¿es la URL del "
                                       "sitio, p. ej. https://tu-sitio.atlassian.net?).") from None
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            if err.code == 401:
                raise RuntimeError("Jira rechazó el correo o el token (401). Vuelve a guardarlos con "
                                   "`worklog jira --configure`.") from None
            raise RuntimeError(f"Jira respondió {err.code} en {method} {path}: {err.reason}") from None

    def myself(self) -> str:
        return self._call("GET", "/rest/api/3/myself")["accountId"]

    def issue(self, key: str) -> dict | None:
        return self._call("GET", f"/rest/api/3/issue/{key}?fields=summary,status,assignee")

    def move(self, key: str, category: str) -> str | None:
        """Aplica la primera transición que lleva a la categoría `indeterminate` o `done`."""
        for t in (self._call("GET", f"/rest/api/3/issue/{key}/transitions") or {}).get("transitions", []):
            if t["to"]["statusCategory"]["key"] == category:
                self._call("POST", f"/rest/api/3/issue/{key}/transitions", {"transition": {"id": t["id"]}})
                return t["to"]["name"]
        return None

    def comment(self, key: str, lines: list[str], comment_id: str | None = None) -> str:
        body = {"body": {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": line}]} for line in lines]}}
        if comment_id:
            res = self._call("PUT", f"/rest/api/3/issue/{key}/comment/{comment_id}", body)
            if res is not None:
                return comment_id  # si lo borraron a mano, se crea otro
        return self._call("POST", f"/rest/api/3/issue/{key}/comment", body)["id"]


def _summary(day: date, project: str, sess: dict) -> list[str]:
    lines = [f"Bitácora · {report.fmt_day(day)} {day.year} · {report.fmt_h(sess['hours'])} activas"
             f" en {project} · {sess['start']:%H:%M}–{sess['end']:%H:%M}",
             f"Sesión: {report._short(sess['title'], 120)}"]
    lines += [f"✅ {report._short(r, 300)}" for r in sess["results"][-3:]]
    if sess["files"]:
        lines.append(f"Archivos editados: {len(sess['files'])}")
    return lines


def _check(jira: Jira, me: str, key: str, cache: dict) -> tuple[dict | None, str]:
    """(issue, motivo); issue es None si la regla «sólo sí» la descarta."""
    if key not in cache:
        issue = jira.issue(key)
        if issue is None:
            cache[key] = (None, "no existe o no tienes acceso")
        elif ((issue["fields"].get("assignee") or {}).get("accountId")) != me:
            who = (issue["fields"].get("assignee") or {}).get("displayName") or "nadie"
            cache[key] = (None, f"no está asignada a ti (responsable: {who})")
        else:
            cache[key] = (issue, "")
    return cache[key]


def _advance(jira: Jira, key: str, issue: dict, closing: bool, dry_run: bool) -> str | None:
    category = issue["fields"]["status"]["statusCategory"]["key"]
    target = "done" if closing and category != "done" else "indeterminate" if category == "new" else None
    if not target:
        return None
    if dry_run:
        return "→ Listo" if target == "done" else "→ En curso"
    moved = jira.move(key, target)
    if moved:
        issue["fields"]["status"]["statusCategory"]["key"] = target
    return f"→ {moved}" if moved else None


def sync(con, start: date, end: date, dry_run: bool = False, home: Path | None = None,
         jira: Jira | None = None, timeout: float = 15.0) -> dict:
    """Vincula las sesiones de [start, end] con sus tareas y avisa a Jira."""
    if jira is None:
        cfg = config(home)
        if not cfg:
            raise RuntimeError("Falta configurar Jira: WORKLOG_JIRA_URL, WORKLOG_JIRA_EMAIL y el token "
                               "(WORKLOG_JIRA_TOKEN o el Llavero, servicio worklog-jira).")
        jira = Jira(*cfg, timeout=timeout)
    con.executescript(SCHEMA)
    store.sync(con, start)
    data = report.collect(con, start, end)
    me, cache = jira.myself(), {}
    linked, skipped, unlinked = [], {}, []

    for day in data["days"]:
        for project, p in day["projects"].items():
            for sess in p["sessions"]:
                worked, closed = evidence(sess)
                ok_keys = []
                for key in sorted(worked):
                    issue, why = _check(jira, me, key, cache)
                    if not issue:
                        skipped[key] = why
                        continue
                    ok_keys.append(key)
                    change = _advance(jira, key, issue, key in closed, dry_run)
                    row = con.execute("SELECT comment_id FROM jira_comments WHERE session_id=? AND issue=?",
                                      (sess["session_id"], key)).fetchone()
                    if not dry_run:
                        cid = jira.comment(key, _summary(day["day"], project, sess), row and row["comment_id"])
                        con.execute("INSERT OR REPLACE INTO jira_comments VALUES (?,?,?)",
                                    (sess["session_id"], key, cid))
                    linked.append({"clave": key, "tarea": issue["fields"]["summary"],
                                   "dia": day["day"].isoformat(), "sesion": sess["session_id"][:8],
                                   "horas": round(sess["hours"], 2), "estado": change or "sin cambio",
                                   "comentario": ("se actualizaría" if row else "se crearía") if dry_run
                                   else ("actualizado" if row else "creado")})
                if not ok_keys:
                    unlinked.append({"dia": day["day"].isoformat(), "proyecto": project,
                                     "sesion": sess["session_id"][:8], "titulo": report._short(sess["title"], 80),
                                     "horas": round(sess["hours"], 2)})
    # Los commits de `git log` no cuentan por sí solos: en repos compartidos traen los de otras
    # personas, y un «cierra X» ajeno no debe mover tus tareas. Sólo valen los hechos en tus sesiones.
    con.commit()
    return {"desde": start.isoformat(), "hasta": end.isoformat(), "simulacion": dry_run,
            "vinculadas": linked,
            "omitidas": [{"clave": k, "motivo": v} for k, v in sorted(skipped.items())],
            "sin_tarea": unlinked,
            "sin_tarea_horas": round(sum(u["horas"] for u in unlinked), 2)}


def close(key: str, note: str = "", home: Path | None = None, jira: Jira | None = None) -> dict:
    """Marca una tarea tuya como terminada, con una nota opcional. Respeta la regla «sólo sí»."""
    if jira is None:
        cfg = config(home)
        if not cfg:
            raise RuntimeError("Falta configurar Jira (ver worklog_mcp/jira.py).")
        jira = Jira(*cfg)
    issue, why = _check(jira, jira.myself(), key.upper(), {})
    if not issue:
        return {"clave": key.upper(), "ok": False, "motivo": why}
    moved = _advance(jira, key.upper(), issue, True, False)
    if note:
        jira.comment(key.upper(), [note])
    return {"clave": key.upper(), "ok": True, "tarea": issue["fields"]["summary"],
            "estado": moved or "ya estaba terminada"}
