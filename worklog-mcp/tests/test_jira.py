import json
import re
import threading
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from worklog_mcp import jira, publish, store

T0 = datetime(2026, 10, 5, 16, 0, tzinfo=timezone.utc)
YO, OTRA = "acc-yo", "acc-otra"


@pytest.fixture(autouse=True)
def _sin_jira_real(monkeypatch):
    for var in ("WORKLOG_JIRA_URL", "WORKLOG_JIRA_EMAIL", "WORKLOG_JIRA_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(publish, "keychain_token", lambda service="": "")


def _sesion(tmp_path, sid, prompts, shell=(), branch="main"):
    proj = tmp_path / "projects" / "-repo-demo"
    proj.mkdir(parents=True, exist_ok=True)

    def line(minutes, kind, **extra):
        return json.dumps({"type": kind, "timestamp": (T0 + timedelta(minutes=minutes)).isoformat(),
                           "cwd": "/repo/demo", "gitBranch": branch, "sessionId": sid, **extra})

    lines = [line(i * 5, "user", message={"role": "user", "content": p}) for i, p in enumerate(prompts)]
    lines.append(line(len(prompts) * 5, "assistant", message={"content": [
        *({"type": "tool_use", "name": "Bash", "input": {"command": c}} for c in shell),
        {"type": "text", "text": "result: hecho"}]}))
    (proj / f"{sid}.jsonl").write_text("\n".join(lines))


def _ses(**kw):
    base = {"prompts": [], "shell": [], "branch": ""}
    base.update(kw)
    base["prompts"] = [(T0, p) for p in base["prompts"]]
    return base


def test_evidence_only_counts_intent():
    worked, closed = jira.evidence(_ses(prompts=["Trabaja QYCA-16", "¿y DOC-157 de quién es?"]))
    assert worked == {"QYCA-16"} and closed == set()  # la mención de pasada no vincula
    worked, closed = jira.evidence(_ses(prompts=["arranca", "listo, cierra QYCA-16 y QYCA-17"]))
    assert worked == closed == {"QYCA-16", "QYCA-17"}
    worked, _ = jira.evidence(_ses(branch="feat/NET-12-login", shell=["cat x | grep NET-99",
                                                                    "git commit -m 'NET-13 listo'"]))
    assert worked == {"NET-12", "NET-13"}  # el grep no cuenta; el commit sí, y lo cierra
    assert jira.evidence(_ses(shell=["git commit -m 'NET-13 listo'"]))[1] == {"NET-13"}


class FakeJira:
    def __init__(self):
        self.issues = {
            "QYCA-1": {"assignee": YO, "cat": "new"},
            "QYCA-2": {"assignee": YO, "cat": "done"},
            "OTRA-1": {"assignee": OTRA, "cat": "new"},
        }
        self.calls = []

    def handle(self, method, path, body):
        self.calls.append((method, path))
        if path == "/rest/api/3/myself":
            return 200, {"accountId": YO}
        m = re.match(r"/rest/api/3/issue/([A-Z]+-\d+)(.*)", path)
        if not m or m.group(1) not in self.issues:
            return 404, {}
        key, rest = m.groups()
        it = self.issues[key]
        if rest.startswith("?fields"):
            who = {"accountId": it["assignee"], "displayName": "Yo" if it["assignee"] == YO else "Otra"}
            return 200, {"key": key, "fields": {"summary": f"Tarea {key}", "assignee": who,
                                                "status": {"statusCategory": {"key": it["cat"]}}}}
        if rest == "/transitions" and method == "GET":
            return 200, {"transitions": [
                {"id": "11", "to": {"name": "Por hacer", "statusCategory": {"key": "new"}}},
                # Como en el tablero MKT de Basil: el bloqueo va primero y también es «En curso».
                {"id": "15", "to": {"name": "Bloqueado", "statusCategory": {"key": "indeterminate"}}},
                {"id": "16", "to": {"name": "En revisión", "statusCategory": {"key": "indeterminate"}}},
                {"id": "21", "to": {"name": "En curso", "statusCategory": {"key": "indeterminate"}}},
                {"id": "31", "to": {"name": "Listo", "statusCategory": {"key": "done"}}}]}
        if rest == "/transitions":
            it["cat"] = {"11": "new", "15": "indeterminate", "16": "indeterminate", "21": "indeterminate", "31": "done"}[body["transition"]["id"]]
            it["moved_to"] = body["transition"]["id"]
            return 204, None
        if rest == "/comment":
            it.setdefault("comments", []).append(body)
            return 201, {"id": str(len(it["comments"]))}
        if rest.startswith("/comment/"):
            return 200, {"id": rest.rsplit("/", 1)[1]}
        return 404, {}


@pytest.fixture
def fake():
    state = FakeJira()

    class H(BaseHTTPRequestHandler):
        def _go(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n)) if n else None
            status, out = state.handle(self.command, self.path, body)
            raw = json.dumps(out).encode() if out is not None else b""
            self.send_response(status)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        do_GET = do_POST = do_PUT = _go

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    state.client = jira.Jira(f"http://127.0.0.1:{srv.server_port}", "yo@x.mx", "t")
    yield state
    srv.shutdown()


def _con(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "PROJECTS_DIR", tmp_path / "projects")
    return store.connect(tmp_path / "w.db")


DAY = T0.astimezone().date()


def test_sync_links_only_my_existing_tasks(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Avanza QYCA-1, OTRA-1 y NADA-9"])
    _sesion(tmp_path, "s2", ["Revisa la web de otro sistema"])
    con = _con(tmp_path, monkeypatch)
    out = jira.sync(con, DAY, DAY, jira=fake.client)
    [v] = out["vinculadas"]
    assert v["clave"] == "QYCA-1" and v["estado"] == "→ En curso" and v["comentario"] == "creado"
    assert fake.issues["QYCA-1"]["cat"] == "indeterminate"
    assert fake.issues["OTRA-1"]["cat"] == "new"  # de otra persona: intacta
    motivos = {o["clave"]: o["motivo"] for o in out["omitidas"]}
    assert "no está asignada a ti" in motivos["OTRA-1"] and "no existe" in motivos["NADA-9"]
    assert [u["sesion"] for u in out["sin_tarea"]] == ["s2"]


def test_resync_updates_the_same_comment(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Avanza QYCA-1"])
    con = _con(tmp_path, monkeypatch)
    jira.sync(con, DAY, DAY, jira=fake.client)
    out = jira.sync(con, DAY, DAY, jira=fake.client)
    assert out["vinculadas"][0]["comentario"] == "actualizado"
    assert len(fake.issues["QYCA-1"]["comments"]) == 1
    assert ("PUT", "/rest/api/3/issue/QYCA-1/comment/1") in fake.calls


def test_never_moves_to_blocked_nor_overrides_a_manual_move(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Avanza QYCA-1"])
    con = _con(tmp_path, monkeypatch)
    jira.sync(con, DAY, DAY, jira=fake.client)
    assert fake.issues["QYCA-1"]["moved_to"] == "21"  # «En curso», ni «Bloqueado» ni «En revisión»
    fake.issues["QYCA-1"]["cat"] = "new"  # alguien la regresa a «Por hacer» a mano
    out = jira.sync(con, DAY, DAY, jira=fake.client)
    assert out["vinculadas"][0]["estado"] == "sin cambio"
    assert fake.issues["QYCA-1"]["cat"] == "new"


def test_comment_only_sync_leaves_status_alone(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Avanza QYCA-1", "cierra QYCA-1"])
    out = jira.sync(_con(tmp_path, monkeypatch), DAY, DAY, jira=fake.client, move=False)
    assert out["vinculadas"][0]["estado"] == "sin cambio" and out["vinculadas"][0]["comentario"] == "creado"
    assert fake.issues["QYCA-1"]["cat"] == "new"
    assert not [c for c in fake.calls if c[1].endswith("/transitions") and c[0] == "POST"]


def test_dry_run_writes_nothing(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Avanza QYCA-1", "cierra QYCA-1"])
    con = _con(tmp_path, monkeypatch)
    out = jira.sync(con, DAY, DAY, dry_run=True, jira=fake.client)
    assert out["vinculadas"][0]["estado"] == "→ Listo"
    assert not [c for c in fake.calls if c[0] in ("POST", "PUT")]


def test_never_reopens_and_close_respects_owner(tmp_path, monkeypatch, fake):
    _sesion(tmp_path, "s1", ["Retoma QYCA-2"])
    jira.sync(_con(tmp_path, monkeypatch), DAY, DAY, jira=fake.client)
    assert fake.issues["QYCA-2"]["cat"] == "done"
    assert jira.close("otra-1", jira=fake.client)["ok"] is False
    assert jira.close("QYCA-1", "Terminado", jira=fake.client)["estado"] == "→ Listo"
    assert fake.issues["QYCA-1"]["cat"] == "done"


def test_config_reads_file_and_needs_all_three(tmp_path, monkeypatch):
    assert jira.config(tmp_path) is None
    (tmp_path / "jira.json").write_text(json.dumps({"url": "https://b.atlassian.net/", "email": "yo@x.mx"}))
    assert jira.config(tmp_path) is None  # falta el token
    monkeypatch.setattr(publish, "keychain_token", lambda service="": "tok" if service == "worklog-jira" else "")
    assert jira.config(tmp_path) == ("https://b.atlassian.net", "yo@x.mx", "tok")


def test_configure_saves_only_a_working_token(tmp_path, fake):
    url = fake.client.url
    saved = []
    largo = "ATATT" + "x" * 187  # más de 128: el aviso de `security` lo habría recortado
    out = jira.configure(tmp_path, prompt=lambda _, r=iter([url, "yo@x.mx"]): next(r), secret=lambda _: largo,
                         save_token=saved.append)
    assert out["ok"] and out["token_caracteres"] == 192 and saved == [largo]
    assert json.loads((tmp_path / "jira.json").read_text()) == {"url": url, "email": "yo@x.mx"}


def test_configure_rejects_a_bad_token_without_saving(tmp_path, monkeypatch):
    def rechaza(self, method, path, body=None):
        raise RuntimeError("Jira rechazó el correo o el token (401).")
    monkeypatch.setattr(jira.Jira, "_call", rechaza)
    saved = []
    with pytest.raises(RuntimeError, match="401"):
        jira.configure(tmp_path, prompt=lambda _, r=iter(["https://b.atlassian.net", "yo@x.mx"]): next(r),
                       secret=lambda _: "malo", save_token=saved.append)
    assert saved == [] and not (tmp_path / "jira.json").exists()


def test_site_accepts_any_page_url():
    assert jira.site("https://basilsoluciones.atlassian.net/jira/for-you?tab=assigned") == \
        "https://basilsoluciones.atlassian.net"
    assert jira.site("basilsoluciones.atlassian.net/") == "https://basilsoluciones.atlassian.net"
