import json
import threading
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from worklog_mcp import publish, report, store
from test_worklog import _transcript


@pytest.fixture(autouse=True)
def _sin_panel(monkeypatch):
    # Que la configuración real de la máquina nunca mande nada desde los tests.
    monkeypatch.delenv("WORKLOG_PANEL_URL", raising=False)
    monkeypatch.delenv("WORKLOG_PANEL_TOKEN", raising=False)
    monkeypatch.setattr(publish, "keychain_token", lambda service=publish.KEYCHAIN_SERVICE: "")


def _dia_demo(tmp_path):
    _transcript(tmp_path)
    con = store.connect(tmp_path / "w.db")
    store.sync(con, date(2026, 10, 1), tmp_path / "projects")
    store.add_entry(con, "decision", "Usar Neon", "", "demo", 0.5, date(2026, 10, 5))
    day = datetime(2026, 10, 5, 16, 0, tzinfo=timezone.utc).astimezone().date()
    return con, day


def test_build_days_matches_panel_contract(tmp_path):
    con, day = _dia_demo(tmp_path)
    [d] = publish.build_days(report.collect(con, day, day))
    assert d["dia"] == day.isoformat()
    assert d["horas"] == pytest.approx(0.25)
    [p] = d["proyectos"]
    assert p["nombre"] == "demo"
    [s] = p["sesiones"]
    assert s["id"] == "abc" and s["rama"] == "main" and s["tipo"] == "bg"
    assert s["resultados"] == ["pagos corregido y probado"]
    assert s["archivos"] == ["pagos.py"]
    assert s["worktree"] is True
    assert s["primera"] == "Revisa el módulo de pagos"
    assert "shell" not in s and "git commit" not in json.dumps(d)  # los comandos no salen
    assert d["entradas"] == [{"tipo": "decision", "titulo": "Usar Neon", "cuerpo": "", "proyecto": "demo", "horas": 0.5}]


def test_config_env_wins_over_file(tmp_path, monkeypatch):
    assert publish.config(tmp_path) is None
    (tmp_path / "panel.json").write_text(json.dumps({"url": "https://a.mx/", "token": "t1"}))
    assert publish.config(tmp_path) == ("https://a.mx", "t1")
    # El Llavero gana sobre el token del JSON: así el archivo sólo necesita la URL.
    monkeypatch.setattr(publish, "keychain_token", lambda service=publish.KEYCHAIN_SERVICE: "llavero")
    assert publish.config(tmp_path) == ("https://a.mx", "llavero")
    monkeypatch.setenv("WORKLOG_PANEL_URL", "http://localhost:4321")
    monkeypatch.setenv("WORKLOG_PANEL_TOKEN", "t2")
    assert publish.config(tmp_path) == ("http://localhost:4321", "t2")


def _server(status=200, reply=None):
    got = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            got.append((self.path, self.headers["Authorization"], json.loads(body)))
            out = json.dumps(reply or {"ok": True}).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, got


def test_publish_posts_days_with_bearer(tmp_path, monkeypatch):
    con, day = _dia_demo(tmp_path)
    monkeypatch.setattr(store, "PROJECTS_DIR", tmp_path / "projects")
    srv, got = _server()
    try:
        monkeypatch.setenv("WORKLOG_PANEL_URL", f"http://127.0.0.1:{srv.server_port}")
        monkeypatch.setenv("WORKLOG_PANEL_TOKEN", "secreto")
        out = publish.publish(con, day, day)
    finally:
        srv.shutdown()
    assert out["dias"] == 1
    [(path, auth, body)] = got
    assert path == "/api/bitacora/dias" and auth == "Bearer secreto"
    assert body["dias"][0]["dia"] == day.isoformat()


def test_publish_reports_panel_errors(tmp_path, monkeypatch):
    con, day = _dia_demo(tmp_path)
    monkeypatch.setattr(store, "PROJECTS_DIR", tmp_path / "projects")
    srv, _ = _server(400, {"ok": False, "error": "No se puede guardar.", "problemas": ["dias[0].dia mal"]})
    try:
        monkeypatch.setenv("WORKLOG_PANEL_URL", f"http://127.0.0.1:{srv.server_port}")
        monkeypatch.setenv("WORKLOG_PANEL_TOKEN", "x")
        with pytest.raises(RuntimeError, match="400.*dias\\[0\\].dia mal"):
            publish.publish(con, day, day)
    finally:
        srv.shutdown()


def test_publish_without_config_says_what_is_missing(tmp_path, monkeypatch):
    con, day = _dia_demo(tmp_path)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path / "vacio")
    with pytest.raises(RuntimeError, match="WORKLOG_PANEL_URL"):
        publish.publish(con, day, day)
