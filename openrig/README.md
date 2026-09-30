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

## Edges are validated, not enforced

`rig spec validate` accepts a rig's `edges`, but OpenRig 0.6.2 does **not**
materialise them into runtime state — `/api/rigs` carries no edge data, and a
`rig send` reaches any seat regardless of the graph.

So the topology is a declaration that `scripts/validate.py` holds the repo to
(a specialist-to-specialist `delegates_to` fails CI), and at run time the
handoff rules live in `rigs/CULTURE.md` and each agent's Boundaries. Useful,
and not a runtime constraint — an earlier revision of this README claimed
otherwise.

## Operating it: things that cost an hour to learn

- **One `rig` operation at a time.** A six-seat launch takes longer than the
  CLI's 120s patience, so the CLI prints a daemon timeout while the launch is
  still running. Issuing another command during that window produced
  `HTTP 500 import_rig`, two rigs with the same name, and six half-launched
  seats. `rig ps` is the truth, not the CLI's exit message.
- **A single-seat launch returns in about ten seconds**, cleanly. `devops-lead`
  plus `rig grow` is genuinely pleasant; the full roster is where the timeout
  appears.
- **`rig down <name>` leaves the record**, and a later launch of the same name
  fails. `rig down <name> --delete` frees it. With two records sharing a name,
  the CLI refuses by name and wants the id — deliberately.
- **`rig up` opens no windows.** It creates detached tmux sessions. Views come
  from `rig terminal open <rig>` (herdr is the default provider) or
  `rig tui --shared`.
- **`rig terminal` needs herdr already running**, since it drives it over a
  control socket; otherwise `available: false, "herdr control socket is not
  answering ping"`. There is no config key to auto-open a view, so wrap it:

  ```bash
  rigup() {
    local spec="$1"; shift
    local name; name=$(awk '/^name:/{print $2; exit}' "$spec")
    rig up "$spec" --yes --cwd "${RIG_CWD:-$PWD}" "$@" || return 1
    rig terminal open "$name"
  }
  ```

- **Seats default to the rig directory**, not the repo root — pass `--cwd` or
  they work in a folder containing only `rig.yaml`.
- **`ui.timezone` defaults to `America/Los_Angeles`**; set it or every
  timestamp misleads.

## Two things found by actually booting it

**Skills are not referenced by name.** `uses.skills` resolves against an
agent's **declared resources**, and resource paths may not contain `..` — so
declaring a plugin's hub skill would mean copying every action and standard
into each agent directory. The generated `agent.yaml` therefore declares only
`guidance/role.md`. The hub skill still loads, because a seat runs the harness
with this marketplace installed and `role.md` carries the agent's own Skills
table. Referenced, never copied — through the harness rather than through
OpenRig.

`culture_file` rejects `..` for the same reason, so each rig directory gets a
generated copy of `rigs/CULTURE.md`, drift-checked like the rest.

**A seat's role is also projected into a managed block in the workspace
`CLAUDE.md`.** Seats sharing one `cwd` therefore overwrite each other, and the
file ends up holding whichever seat attached last. The authoritative delivery
is `startup.files` with `delivery_hint: send_text`, which is per session — but
if it matters that each seat's `CLAUDE.md` matches its own role, give the seats
distinct working directories. `.openrig/` and a managed `CLAUDE.md` appear in
the seat's cwd at launch; both are gitignored here.

## Before the first boot: answer the prompts, or they stall the fleet

Every seat came up blocked on Claude Code's project MCP-server prompt:

```
3 new MCP servers found in this project
Space to select · Esc to reject all
```

All twelve sat there until answered — `Readiness timeout after 30s`. Nothing
about this is OpenRig's fault; it is what an interactive prompt does when
nobody is at the terminal. Decide once, in `~/.claude/settings.json`:

```json
"enableAllProjectMcpServers": false
```

or list the servers you want enabled, so a seat never has to ask. Then
`rig ps --nodes -A` should show every seat `run` with no reason.

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
