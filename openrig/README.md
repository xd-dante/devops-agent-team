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

## The mutation gate

`plugins/devops/hooks/gate.py` runs on `PreToolUse` for `Bash` and decides
without a human present. That is the point: an unattended seat has nobody at
its terminal to answer a permission prompt, so a prompt either stalls the seat
or gets allowlisted away.

**File edits are untouched.** Writing Terraform, charts and code is the work.
The gate refuses a narrow set of commands:

| Refused | Why |
|---------|-----|
| `terraform apply`/`plan` without `-target`, any `destroy`, `state rm/mv/push` | blast radius beyond the change; state surgery is not reversible from here |
| `kubectl` mutations, `exec`, `port-forward`, `rollout restart` | desired state lives in git |
| force-push, push to `develop`/`main`/`master`, remote branch deletion | protected history |
| `argocd app sync`, `kargo promote` | gated single-target actions |
| `--dangerously-skip-permissions`, `danger-full-access` | removes every check for the rest of the session |

Every denial names the escalation path, so a blocked seat reports upward rather
than stalling.

Protected-branch matching parses the **refspec**, not the command string: a
`\b` boundary treats `-` and `/` as word edges, so `feat/main-nav` and
`develop-fix` look like protected branches to a naive regex. They are pushable;
`tests/test_gate.py` covers them.

Run the tests — both directions, because a gate that denies everything is as
useless as none:

```bash
python3 tests/test_gate.py    # 19 allow, 25 deny, 4 non-Bash
```

`scripts/validate.py` warns if a rig contains a `gated` or `mutating` seat while
no plugin ships gate hooks.

## What OpenRig writes to your machine

Before running it, read upstream's own list. It writes tmux config, workspace
trust and onboarding state, `.claude/settings.local.json` hooks and statusLine,
can modify `.mcp.json`, writes Codex hooks and trust hashes, and relays
activity events (event type, seat identity, timestamps — not prompt text or
tool arguments) to its daemon. Requires Node 22/24 and tmux; no native Windows.
