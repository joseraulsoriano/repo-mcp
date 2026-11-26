import subprocess
from datetime import date, datetime, timedelta, timezone

from worklog_mcp import ciclo, publish, store


def _repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    g = lambda *a, **env: subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True,
                                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
                                               "HOME": str(tmp_path), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                                               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", **env})
    g("init", "-q", "-b", "main")
    for i, msg in enumerate(["feat: uno [KAN-1]", "feat: dos [KAN-2]", "fix: tres [KAN-2]"]):
        (r / f"f{i}").write_text(str(i))
        g("add", ".")
        g("commit", "-q", "-m", msg)
        if i == 0:
            g("tag", "-a", "v2026.11.24", "-m", "pub")
    g("tag", "-a", "v2026.11.25", "-m", "pub")
    g("tag", "-a", "no-es-publicacion", "-m", "x")
    return r


def test_publicaciones_trae_solo_lo_nuevo_de_cada_tag(tmp_path):
    r = _repo(tmp_path)
    roots = store.repo_roots([str(r)])
    hoy = date.today()
    pubs = ciclo.publicaciones(roots, hoy - timedelta(days=1), hoy + timedelta(days=1), store.project_of)
    assert [p["tag"] for p in pubs] == ["v2026.11.24", "v2026.11.25"]
    assert len(pubs[0]["shas"]) == 1 and len(pubs[1]["shas"]) == 2
    assert pubs[1]["proyecto"] == "repo"


def test_bug_se_cierra_con_el_fix_que_lo_menciona(tmp_path):
    con = store.connect(tmp_path / "w.db")
    ahora = datetime.now(timezone.utc)
    a = ciclo.abrir_bug(con, "Cotizaciones da 500", "repo", "KAN-138", cuando=ahora - timedelta(hours=2))
    b = ciclo.abrir_bug(con, "Icono sin pintar", "repo", cuando=ahora - timedelta(hours=2))
    otro = ciclo.abrir_bug(con, "En otro repo", "otro", "KAN-138", cuando=ahora - timedelta(hours=2))
    commits = [
        {"sha": "a1", "ts": ahora - timedelta(hours=3), "subject": "fix: antes de anotarlo [KAN-138]", "project": "repo"},
        {"sha": "a2", "ts": ahora - timedelta(hours=1), "subject": "feat: no es arreglo [KAN-138]", "project": "repo"},
        {"sha": "a3", "ts": ahora, "subject": "fix(ventas): etapa Diseño [KAN-138]", "project": "repo"},
        {"sha": "a4", "ts": ahora, "subject": "fix(ui): icono BUG-%d" % b, "project": "repo"},
    ]
    assert sorted(ciclo.cerrar_bugs(con, commits)) == sorted([a, b])
    assert ciclo.cerrar_bugs(con, commits) == []  # idempotente
    abiertos = ciclo.listar_bugs(con)
    assert [x["id"] for x in abiertos] == [otro]
    cerrado = {x["id"]: x for x in ciclo.listar_bugs(con, "cerrados")}[a]
    assert cerrado["fix_sha"] == "a3"


def test_bug_necesita_titulo_y_proyecto(tmp_path):
    con = store.connect(tmp_path / "w.db")
    try:
        ciclo.abrir_bug(con, " ", "repo")
    except ValueError:
        pass
    else:
        raise AssertionError("debió rechazarse")


class _JiraFalsa:
    def __init__(self, fichas, url="https://rtc"):
        self.fichas, self.url, self.preguntas = fichas, url, []

    def ficha(self, clave):
        self.preguntas.append(clave)
        return self.fichas.get(clave)


def test_cada_ticket_se_pregunta_solo_al_sitio_de_su_prefijo(tmp_path):
    con = store.connect(tmp_path / "w.db")
    rtc = _JiraFalsa({"KAN-139": {"creado": "2026-11-25T23:46:27+00:00", "epica": False},
                      "KAN-9": {"creado": "2026-11-10T10:00:00+00:00", "epica": True}})
    basil = _JiraFalsa({"CLIEN-1": {"creado": "2025-11-23T03:06:35+00:00", "epica": False}}, "https://basil")
    sitios = [({"KAN", "HAC"}, rtc), ({"BAS"}, basil)]
    r = ciclo.fechas_tickets(con, {"KAN-139", "KAN-9", "CLIEN-1", "CAR-9"}, sitios)
    assert r == {"KAN-139": {"creado": "2026-11-25T23:46:27+00:00", "epica": False},
                 "KAN-9": {"creado": "2026-11-10T10:00:00+00:00", "epica": True}}
    assert basil.preguntas == []  # CLIEN no es de Basil aquí: no se adivina con otro sitio
    assert sorted(rtc.preguntas) == ["KAN-139", "KAN-9"]
    ciclo.fechas_tickets(con, {"KAN-139", "KAN-9"}, sitios)
    assert sorted(rtc.preguntas) == ["KAN-139", "KAN-9"]  # ya guardadas: no se vuelven a pedir


def test_un_404_se_reintenta_hasta_el_dia_siguiente(tmp_path):
    con = store.connect(tmp_path / "w.db")
    rtc = _JiraFalsa({})
    sitios = [({"KAN"}, rtc)]
    ciclo.fechas_tickets(con, {"KAN-404"}, sitios)
    ciclo.fechas_tickets(con, {"KAN-404"}, sitios)
    assert rtc.preguntas == ["KAN-404"]
    ciclo.fechas_tickets(con, {"KAN-404"}, sitios, ahora=datetime.now(timezone.utc) + timedelta(days=2))
    assert rtc.preguntas == ["KAN-404", "KAN-404"]


def test_claves_de_ignora_lo_que_no_es_ticket():
    data = {"days": [{"commits": [{"subject": "fix: UTF-8 y SHA-256 en el CSV [KAN-7] BUG-3"}]}]}
    assert publish.claves_de(data) == {"KAN-7"}


def test_build_days_lleva_tickets_publicaciones_y_bugs():
    ts = datetime(2026, 11, 25, 18, 0, tzinfo=timezone.utc)
    data = {"days": [{"day": date(2026, 11, 25), "hours": 0, "projects": {}, "entries": [],
                      "commits": [{"sha": "s1", "ts": ts, "project": "repo", "subject": "feat: x [KAN-139]"}],
                      "publicaciones": [{"proyecto": "repo", "tag": "v2026.11.25.4", "ts": ts, "shas": ["s1"]}],
                      "bugs": [{"id": 1, "proyecto": "repo", "ticket": "", "titulo": "t", "abierto": "a",
                                "cerrado": "", "fix": ""}]}]}
    [d] = publish.build_days(data, {"KAN-139": {"creado": "2026-11-25T23:46:27+00:00", "epica": False}})
    assert d["commits"][0]["tickets"] == [{"clave": "KAN-139", "creado": "2026-11-25T23:46:27+00:00", "epica": False}]
    assert d["publicaciones"][0]["tag"] == "v2026.11.25.4" and d["publicaciones"][0]["shas"] == ["s1"]
    assert d["bugs"][0]["id"] == 1
