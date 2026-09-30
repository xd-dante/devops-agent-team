#!/usr/bin/env python3
"""Mechanical checks for the plugin tree.

Run from the repo root:  python3 scripts/validate.py

Checks:
  1. every JSON file parses
  2. every marketplace `source` resolves to a real plugin.json
  3. every SKILL.md and agent file has name + description frontmatter
  4. every relative markdown link resolves
  5. every agent named in the routing table exists on disk
  6. no site-specific values or credential-shaped strings are committed
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules"}
errors: list[str] = []
warnings: list[str] = []


def md_files() -> list[Path]:
    return [p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.parts)]


def check_json() -> None:
    for f in ROOT.rglob("*.json"):
        if SKIP_DIRS & set(f.parts):
            continue
        try:
            json.loads(f.read_text())
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid JSON: {f.relative_to(ROOT)}: {exc}")


def check_marketplace() -> None:
    mp = ROOT / ".claude-plugin" / "marketplace.json"
    if not mp.exists():
        errors.append("missing .claude-plugin/marketplace.json")
        return
    data = json.loads(mp.read_text())
    for plugin in data.get("plugins", []):
        src = ROOT / plugin["source"].lstrip("./")
        if not (src / ".claude-plugin" / "plugin.json").exists():
            errors.append(f"marketplace: {plugin['name']} -> missing {src}/.claude-plugin/plugin.json")
    declared = {p["name"] for p in data.get("plugins", [])}
    on_disk = {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()}
    for name in sorted(on_disk - declared):
        errors.append(f"plugin on disk but not in marketplace: {name}")


def check_frontmatter() -> None:
    targets = list(ROOT.rglob("SKILL.md")) + list(ROOT.rglob("agents/*.md"))
    for f in targets:
        if SKIP_DIRS & set(f.parts):
            continue
        text = f.read_text()
        rel = f.relative_to(ROOT)
        if not text.startswith("---\n"):
            errors.append(f"missing frontmatter: {rel}")
            continue
        block = text.split("---\n", 2)[1]
        for key in ("name:", "description:"):
            if key not in block:
                errors.append(f"frontmatter missing {key!r}: {rel}")


def check_links() -> None:
    pattern = re.compile(r"\[[^\]]+\]\((?!https?:|mailto:)([^)#]+)")
    for f in md_files():
        for match in pattern.finditer(f.read_text()):
            href = match.group(1)
            if any(c in href for c in "<>{}"):
                continue  # templated placeholder, not a real link
            target = (f.parent / href).resolve()
            if not target.exists():
                errors.append(f"dead link in {f.relative_to(ROOT)}: {match.group(1)}")


def check_routing_table() -> None:
    table = ROOT / "plugins/devops/skills/orchestrate/standards/routing-table.md"
    if not table.exists():
        errors.append("missing routing-table.md")
        return
    text = table.read_text()

    # every agent that exists on disk, by its frontmatter name
    on_disk: set[str] = set()
    for f in ROOT.rglob("agents/*.md"):
        block = f.read_text().split("---\n", 2)[1]
        found = re.search(r"^name:\s*(\S+)", block, re.M)
        if found:
            on_disk.add(found.group(1))

    # backticked tokens in the table that look like an agent but do not exist,
    # ignoring any the table explicitly says does not exist
    backticked = set(re.findall(r"`([a-z][a-z0-9-]{3,})`", text))
    for name in sorted(backticked & {n for n in backticked if n.endswith(("-agent", "-lead", "-analyst",
                                    "-engineer", "-investigator", "-analyzer", "-promoter"))}):
        if name not in on_disk and not re.search(rf"no\s+`?{re.escape(name)}`?", text):
            errors.append(f"routing table references unknown agent: {name}")

    # the lead agent is the dispatcher, not a dispatch target
    for name in sorted(on_disk - backticked - {"ops-lead"}):
        warnings.append(f"agent not in routing table (never dispatched): {name}")


# Patterns that must never be committed to a public repo. Generic shapes only —
# this list deliberately contains no real organisation's values.
FORBIDDEN = [
    (r"\b\d{12}\b", "12-digit number — looks like a cloud account id"),
    (r"[a-z0-9-]+\.atlassian\.net", "tracker hostname"),
    (r"\b[A-Za-z0-9._%+-]+@(?!example\.(com|org)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "email address"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"(?i)\bghp_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?i)\b(password|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"<{$]{8,}", "hardcoded credential"),
    (r"/Users/[a-z0-9._-]+/", "absolute home path"),
    (r"arn:aws:[a-z0-9-]*:[a-z0-9-]*:\d{12}", "ARN with account id"),
]


def check_memory_not_committed() -> None:
    """Real memory entries are site-specific by design and must stay local."""
    mem = ROOT / "memory"
    if not mem.exists():
        return
    allowed = {"README.md", ".gitignore"}
    for f in mem.rglob("*"):
        if f.is_dir() or SKIP_DIRS & set(f.parts):
            continue
        if f.name in allowed or f.name.endswith(".example"):
            continue
        errors.append(
            f"real memory file committed (must stay local): {f.relative_to(ROOT)}"
        )


def check_forbidden() -> None:
    allow = re.compile(r"example|placeholder|<[a-z-]+>|\{[a-z_]+\}|your-org", re.I)
    for f in md_files() + [p for p in ROOT.rglob("*.yml") if not SKIP_DIRS & set(p.parts)]:
        for lineno, line in enumerate(f.read_text().splitlines(), 1):
            for pattern, label in FORBIDDEN:
                if re.search(pattern, line) and not allow.search(line):
                    errors.append(
                        f"{label} in {f.relative_to(ROOT)}:{lineno}: {line.strip()[:90]}"
                    )


def check_openrig_projection() -> None:
    """openrig/agents is generated; a hand edit there is silently lost."""
    gen = ROOT / "scripts/gen-openrig.py"
    if not gen.is_file() or not (ROOT / "openrig/agents").is_dir():
        return
    import subprocess
    r = subprocess.run([sys.executable, str(gen), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        detail = (r.stderr or r.stdout).strip().replace("\n", "; ")
        errors.append(f"openrig projection is stale — run scripts/gen-openrig.py ({detail})")


def _rig_access_classes() -> dict[str, str]:
    """agent name -> access class, read from the generated agent.yaml headers."""
    out = {}
    for y in (ROOT / "openrig/agents").glob("*/agent.yaml"):
        m = re.search(r"^# access: (\w+)", y.read_text(encoding="utf-8"), re.M)
        if m:
            out[y.parent.name] = m.group(1)
    return out


def check_rigs() -> None:
    """The rig topology carries the handoff contract. Verify it actually does.

    Flow-style edges (`{kind: x, from: a, to: b}`) are matched directly so the
    check needs no YAML dependency in CI.
    """
    rigs = sorted((ROOT / "rigs").glob("*/rig.yaml")) if (ROOT / "rigs").is_dir() else []
    if not rigs:
        return
    access = _rig_access_classes()
    for rig in rigs:
        text = rig.read_text(encoding="utf-8")
        rel = rig.relative_to(ROOT)

        # every agent_ref resolves to a generated agent
        refs = {}
        for m in re.finditer(r'agent_ref:\s*"local:([^"]+)"', text):
            target = (rig.parent / m.group(1)).resolve()
            name = target.name
            refs[name] = target
            if not (target / "agent.yaml").is_file():
                errors.append(f"{rel}: agent_ref does not resolve: {m.group(1)}")

        # the orchestrator seat: the only legal source of delegates_to
        lead_ids = {f"{pod}.{mid}" for pod, mid in re.findall(
            r"- id: (\w+)\n(?:.*\n)*?      - id: (\w+)\n        agent_ref: \"local:[^\"]*ops-lead\"", text)}
        lead_seats = lead_ids or {"orch.lead"}

        for kind, src, dst in re.findall(
                r"\{kind:\s*(\w+),\s*from:\s*([\w.]+),\s*to:\s*([\w.]+)\}", text):
            if kind == "delegates_to" and src not in lead_seats:
                errors.append(
                    f"{rel}: delegates_to from {src} to {dst} — writes must not chain "
                    f"between specialists; only {'/'.join(sorted(lead_seats))} may delegate")
            if kind not in {"delegates_to", "can_observe", "escalates_to"}:
                warnings.append(f"{rel}: unknown edge kind {kind!r}")

        # a seat that can mutate should not exist while the gates are only prose
        gate_hooks = list(ROOT.glob("plugins/*/hooks/*.json"))
        for name in sorted(refs):
            klass = access.get(name)
            if klass in {"gated", "mutating"} and name != "ops-lead" and not gate_hooks:
                warnings.append(
                    f"{rel}: seat {name!r} is {klass} but no gate hooks exist yet — "
                    f"a managed seat runs with acceptEdits, which prose boundaries do not survive")


def main() -> int:
    for check in (
        check_json,
        check_marketplace,
        check_frontmatter,
        check_links,
        check_routing_table,
        check_memory_not_committed,
        check_forbidden,
    ):
        check()
    check_openrig_projection()
    check_rigs()

    for warning in warnings:
        print(f"warn:  {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"\n{len(errors)} error(s)")
        return 1
    print(f"\nvalidation clean ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
