# OpenRig projection

`openrig/agents/` is **generated**. The plugins are the source of truth.

```bash
python3 scripts/gen-openrig.py           # regenerate
python3 scripts/gen-openrig.py --check   # fail if stale (runs in CI)
```

Each agent becomes `agent.yaml` plus `guidance/role.md`, where `uses.skills`
points at the hub skill that already exists in the plugin. **No action or
standard is duplicated** — the 40-plus action files and 30-plus standards are
referenced, not copied.

Agent → hub skill comes from
`plugins/devops/skills/orchestrate/standards/routing-table.md`, not from the
directory layout: one plugin can own several hub skills, and an agent missing
from the routing table is never dispatched, so it gets no seat either.

## Access classes

Read off each agent's own `description`, never hardcoded:

| Class | Meaning | Seat today |
|-------|---------|------------|
| `strict` | strictly read-only | ✅ in `rigs/devops-readonly` |
| `gated` | read-only apart from one gated mutation | ❌ waiting on hook-enforced gates |
| `mutating` | changes files, repos or infrastructure | ❌ waiting on hook-enforced gates |

## Why the mutating seats have no rig yet

A managed OpenRig seat runs with `permissions.defaultMode: acceptEdits` and a
pre-trusted workspace. Every "⚠️ Ask first" and gated precondition in this repo
is **prose in an agent's Boundaries section**, and prose is not enforcement. Put
differently: the gates that make `terraform-engineer` safe interactively do not
survive being run as an auto-accepting seat.

Those gates have to move somewhere a seat cannot relax — `PreToolUse` hooks —
before a mutating seat is worth launching. Until then `rigs/devops-readonly`
exercises routing, topology and reporting with nothing that can write.

## What OpenRig writes to your machine

Before running it, read upstream's own list. It writes tmux config, workspace
trust and onboarding state, `.claude/settings.local.json` hooks and statusLine,
can modify `.mcp.json`, writes Codex hooks and trust hashes, and relays
activity events (event type, seat identity, timestamps — not prompt text or
tool arguments) to its daemon. Requires Node 22/24 and tmux; no native Windows.
