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
    table = ROOT / "plugins/orchestrator/skills/task-orchestration/standards/routing-table.md"
    if not table.exists():
        errors.append("missing routing-table.md")
        return
    text = table.read_text()
    referenced = {
        name
        for name in re.findall(r"`([a-z0-9-]+-agent)`", text)
        if not re.search(rf"no\s+`{re.escape(name)}`", text)
    }
    on_disk: set[str] = set()
    for f in ROOT.rglob("agents/*.md"):
        block = f.read_text().split("---\n", 2)[1]
        found = re.search(r"^name:\s*(\S+)", block, re.M)
        if found:
            on_disk.add(found.group(1))
    for name in sorted(referenced - on_disk):
        errors.append(f"routing table references unknown agent: {name}")
    for name in sorted(on_disk - referenced - {"devops-orchestrator"}):
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
