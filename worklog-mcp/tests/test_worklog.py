import json
from datetime import date, datetime, timedelta, timezone

from worklog_mcp import ingest, report, store

T0 = datetime(2026, 10, 5, 16, 0, tzinfo=timezone.utc)


def _line(minutes, kind, **extra):
    return json.dumps({"type": kind, "timestamp": (T0 + timedelta(minutes=minutes)).isoformat(),
                       "cwd": "/repo/demo/.claude/worktrees/x", "gitBranch": "main", "sessionKind": "bg",
                       "sessionId": "abc", **extra})


def _transcript(tmp_path):
    proj = tmp_path / "projects" / "-repo-demo"
    proj.mkdir(parents=True)
    lines = [
        json.dumps({"type": "ai-title", "aiTitle": "Demo de bitácora"}),
        _line(0, "user", message={"role": "user", "content": "<local-command-caveat>x</local-command-caveat>"}, isMeta=True),
        _line(0, "user", message={"role": "user", "content": "Revisa el módulo de pagos"}),
        _line(5, "assistant", message={"content": [
            {"type": "tool_use", "name": "Edit", "input": {"file_path": "/repo/demo/.claude/worktrees/x/pagos.py"}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m 'fix pagos'"}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls -la"}},
            {"type": "tool_use", "name": "Skill", "input": {"skill": "review"}},
        ]}),
        _line(10, "user", message={"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}),
        _line(12, "assistant", message={"content": [{"type": "text", "text": "Listo.\nresult: pagos corregido y probado"}]}),
        # Hueco de 2 h: no debe contar como trabajo.
        _line(132, "user", message={"role": "user", "content": "<command-name>/clear</command-name>"}),
        _line(135, "assistant", message={"content": [{"type": "text", "text": "ok"}]}),
        json.dumps({"type": "cost-state", "totalLinesAdded": 40, "totalLinesRemoved": 3, "totalCostUSD": 1.5}),
    ]
    path = proj / "abc.jsonl"
    path.write_text("\n".join(lines))
    return path


def test_parse_file_extracts_evidence(tmp_path):
    s = ingest.parse_file(_transcript(tmp_path))
    assert s.title == "Demo de bitácora"
    assert [p for _, p in s.prompts] == ["Revisa el módulo de pagos"]
    kinds = {(k, v) for _, k, v in s.actions}
    assert ("edit", "/repo/demo/.claude/worktrees/x/pagos.py") in kinds
    assert ("shell", "git commit -m 'fix pagos'") in kinds
    assert ("skill", "/review") in kinds
    assert ("result", "pagos corregido y probado") in kinds
    assert not any(v == "ls -la" for _, _, v in s.actions)
    assert (s.lines_added, s.lines_removed) == (40, 3)


def test_active_hours_skips_idle_and_parallel_overlap():
    a = [T0 + timedelta(minutes=m) for m in (0, 10, 20)]
    b = [T0 + timedelta(minutes=m) for m in (5, 15)]  # sesión paralela
    assert store.active_hours(a) == 20 / 60
    assert store.active_hours(a + b) == 20 / 60
    assert store.active_hours([T0, T0 + timedelta(hours=2)]) == 0


def test_project_of_maps_worktrees_to_parent():
    assert store.project_of("/x/editor/.claude/worktrees/agentes") == "editor"
    assert store.project_of("") == "(sin proyecto)"


def test_report_end_to_end(tmp_path):
    _transcript(tmp_path)
    con = store.connect(tmp_path / "w.db")
    assert store.sync(con, date(2026, 10, 1), tmp_path / "projects")["reindexados"] == 1
    assert store.sync(con, date(2026, 10, 1), tmp_path / "projects")["reindexados"] == 0
    store.add_entry(con, "Postura", "No migrar a GraphQL", "REST basta", "demo", 1.0, date(2026, 10, 5))
    day = datetime(2026, 10, 5, 16, 0, tzinfo=timezone.utc).astimezone().date()
    md = report.render(report.collect(con, day, day), "completo")
    assert "Demo de bitácora" in md
    assert "✅ pagos corregido y probado" in md
    assert "`pagos.py`" in md
    assert "**15m activas**" in md  # 12 min + 3 min; el hueco de 2 h no cuenta
    assert "[postura]" in md and "No migrar a GraphQL" in md


def test_parse_day_keywords():
    today = date.today()
    assert report.parse_day("hoy") == today
    assert report.parse_day("-3d") == today - timedelta(days=3)
    assert report.parse_day("lunes").weekday() == 0
    assert report.parse_day("2026-10-05") == date(2026, 10, 5)
