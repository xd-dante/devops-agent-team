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

| Class | Meaning |
|-------|---------|
| `strict` | has agreed to read only |
| `gated` | read-only apart from one mutation it must be asked for |
| `mutating` | changes files, repositories or infrastructure |

**A class is a declaration of intent, not a capability limit.** A `strict`
agent holding an administrator profile can delete a production database —
nothing in the class prevents it. The class states what the agent has agreed
to do, which is why the limits are written as behaviour rather than as trust
in the environment. `rigs/devops-readonly` uses only `strict` seats for a
lower-risk first run; `rigs/devops-full` runs all twelve.

## Limits on a mutating seat

Agents edit files freely — that is the work, and `acceptEdits` only
auto-accepts edits. What they must not do lives in each agent's **Boundaries**
section, with four limits carried verbatim by all of them
(`devops/orchestrate/standards/safety-limits.md`): no force-push or push to a
protected branch, no `terraform destroy`, no widening their own permissions,
and **cancel any change whose plan touches resources outside the task**.

`scripts/validate.py` fails if an agent is missing one, so the wording cannot
drift into a lenient variant.

**These are instructions, not enforcement.** An agent follows them because it
read them. Two mechanisms outside the agent compose with this and are worth
having before running unattended seats against anything that matters:

| Mechanism | Covers |
|-----------|--------|
| `permissions.deny` in Claude Code settings | absolute prohibitions — `terraform destroy`, force-push, `kubectl delete`. A permission mode cannot override a deny rule |
| Cloud IAM roles | the real boundary. A read-only role for an investigating seat cannot be argued around, and costs it nothing it needs |

Worth checking your own posture first: `Bash(*)` in `permissions.allow` with an
empty `deny` list means nothing prompts you interactively either, so a seat is
not a new exposure so much as an unsupervised one.

## What OpenRig writes to your machine

Before running it, read upstream's own list. It writes tmux config, workspace
trust and onboarding state, `.claude/settings.local.json` hooks and statusLine,
can modify `.mcp.json`, writes Codex hooks and trust hashes, and relays
activity events (event type, seat identity, timestamps — not prompt text or
tool arguments) to its daemon. Requires Node 22/24 and tmux; no native Windows.
