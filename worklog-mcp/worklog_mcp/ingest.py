"""Parseo de un transcript JSONL de Claude Code a un resumen estructurado.

Un transcript vive en ~/.claude/projects/<proyecto>/<session>.jsonl; los de
subagentes en ~/.claude/projects/<proyecto>/<session>/subagents/agent-*.jsonl.
Sólo se extrae lo que sirve como evidencia de trabajo: cuándo hubo actividad,
qué se pidió, qué se tocó y qué se entregó.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# Comandos de shell que dejan huella verificable (commits, PRs, despliegues).
BASH_EVIDENCE = re.compile(
    r"\b(git (commit|push|merge|tag)|gh pr (create|merge)|gh release|vercel( deploy| --prod)|wrangler deploy|docker (build|push))\b"
)
NOISE_PREFIXES = (
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<task-notification>",
    "<bash-input>",
    "<bash-stdout>",
    "<bash-stderr>",
    "Caveat:",
    "[Request interrupted",
)
TAG_BLOCK = re.compile(r"<(system-reminder|pasted_content[^>]*)>.*?</(system-reminder|pasted_content)>", re.S)
COMMAND_NAME = re.compile(r"<command-name>(.*?)</command-name>", re.S)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
RESULT_LINE = re.compile(r"^\s*(?:\*\*)?result:(?:\*\*)?\s*(.+)$", re.I | re.M)

PROMPT_MAX = 2000
TEXT_MAX = 600


@dataclass
class Session:
    source: str
    session_id: str
    is_subagent: bool
    cwd: str = ""
    git_branch: str = ""
    title: str = ""
    kind: str = ""  # "bg" (trabajo en segundo plano) o interactiva
    activity: list[datetime] = field(default_factory=list)
    prompts: list[tuple[datetime, str]] = field(default_factory=list)
    actions: list[tuple[datetime, str, str]] = field(default_factory=list)  # (ts, tipo, objetivo)
    lines_added: int = 0
    lines_removed: int = 0
    cost_usd: float = 0.0
    last_text: str = ""


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clean_prompt(content) -> str | None:
    """Devuelve el texto que escribió la persona, o None si es ruido del harness."""
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                return None
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        content = "\n".join(parts)
    if not isinstance(content, str):
        return None
    text = content.strip()
    if not text or text.startswith(NOISE_PREFIXES):
        return None
    name = COMMAND_NAME.search(text)
    if name:
        args = COMMAND_ARGS.search(text)
        text = f"{name.group(1).strip()} {args.group(1).strip() if args else ''}".strip()
        if text in ("/clear", "/compact", "/exit", "/resume", "/model", "/config", "/status"):
            return None
    text = TAG_BLOCK.sub("", text).strip()
    if not text:
        return None
    return text[:PROMPT_MAX]


def _action_from_tool(tool: dict) -> tuple[str, str] | None:
    name = tool.get("name", "")
    inp = tool.get("input") or {}
    if name in EDIT_TOOLS:
        path = inp.get("file_path") or inp.get("notebook_path")
        return ("edit", path) if path else None
    if name == "Bash":
        cmd = (inp.get("command") or "").strip()
        if BASH_EVIDENCE.search(cmd):
            return ("shell", cmd.splitlines()[0][:240])
        return None
    if name in ("Agent", "Task"):
        return ("agent", (inp.get("description") or inp.get("subagent_type") or "")[:200])
    if name == "Skill":
        skill = inp.get("skill") or ""
        args = (inp.get("args") or "")[:120]
        return ("skill", f"/{skill} {args}".strip())
    if name == "ReportFindings":
        return ("review", f"{len(inp.get('findings') or [])} hallazgos reportados")
    return None


def parse_file(path: Path) -> Session | None:
    is_sub = path.parent.name == "subagents"
    session_id = path.parent.parent.name if is_sub else path.stem
    s = Session(source=str(path), session_id=session_id, is_subagent=is_sub)
    titles: list[str] = []
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = d.get("type")
            if kind == "ai-title" and d.get("aiTitle"):
                titles.append(d["aiTitle"])
                continue
            if kind == "custom-title" and d.get("customTitle"):
                titles.append(d["customTitle"])
                continue
            if kind == "cost-state":
                # Acumulados de la sesión: nos quedamos con el máximo visto.
                s.lines_added = max(s.lines_added, int(d.get("totalLinesAdded") or 0))
                s.lines_removed = max(s.lines_removed, int(d.get("totalLinesRemoved") or 0))
                s.cost_usd = max(s.cost_usd, float(d.get("totalCostUSD") or 0))
                continue
            if kind not in ("user", "assistant"):
                continue
            ts = parse_ts(d.get("timestamp"))
            if ts is None:
                continue
            s.cwd = s.cwd or d.get("cwd") or ""
            if d.get("gitBranch") and d["gitBranch"] != "HEAD":
                s.git_branch = d["gitBranch"]
            s.kind = s.kind or d.get("sessionKind") or ""
            s.activity.append(ts)
            msg = d.get("message") or {}
            if kind == "user":
                if d.get("isMeta") or is_sub:
                    continue
                text = clean_prompt(msg.get("content"))
                if text:
                    s.prompts.append((ts, text))
                continue
            for block in msg.get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    act = _action_from_tool(block)
                    if act:
                        s.actions.append((ts, *act))
                elif block.get("type") == "text" and block.get("text", "").strip():
                    text = block["text"].strip()
                    s.last_text = text[:TEXT_MAX]
                    for m in RESULT_LINE.finditer(text):
                        s.actions.append((ts, "result", m.group(1).strip()[:400]))
    if not s.activity:
        return None
    if titles:
        s.title = titles[-1]
    return s
