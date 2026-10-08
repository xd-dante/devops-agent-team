# Dispatch Mode

How a specialist is launched, not which one. `routing-table.md` names the
agent; this decides whether it arrives as a subagent, a teammate, or neither.

## The default is subagents, and that is fine

Agent teams are **experimental and off unless enabled**:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

With teams disabled, every rule below collapses to "dispatch a subagent",
which is the behaviour this toolkit was built on. Nothing here requires teams.
Read the rest when they are on, or when deciding whether to turn them on.

## Three modes

| Mode | A worker is | Communication | Coordination | Cost |
|------|-------------|---------------|--------------|------|
| **Subagent** | a helper that returns a result | result to the caller | the lead manages everything | lower — results summarise back |
| **Teammate** | a full, independent session | peers message each other | shared task list, self-claiming, file-locked | linear per teammate |
| **Cross-session** | a session the user started | messages between them | manual | n/a |

Cross-session messaging is not a dispatch mode for this skill — it is how a
user's own sessions talk. Mentioned so it is not confused with the other two.

## Enabling teams changes ordinary delegation

This surprises people, so state it before recommending anything:

| What is spawned | What it becomes, with teams on |
|-----------------|-------------------------------|
| a **named** subagent | a **teammate** — a whole session, at a whole session's cost |
| an unnamed subagent | a subagent |
| a fork, or a call passing `isolation` | a subagent |

Naming is the switch, and names get chosen without being asked for. So with
teams on, expect more teams than intended. If dispatch cost jumps, that is the
mechanism — not a bug.

## Which mode for which agent

The deciding constraint is file conflicts: two teammates editing the same file
overwrite each other, and sequential work with dependencies is slower as a
team than as a chain.

That lines up with each agent's access class, which is read from its own
`description`:

| Class | Agents | Mode | Why |
|-------|--------|------|-----|
| `strict` | `kubernetes-investigator`, `newrelic-analyst`, `aws-investigator`, `aws-cost-analyzer`, `codegraph-navigator` | **teammate** | read-only, genuinely parallel, and they improve by challenging each other |
| `gated` | `argocd-analyst`, `kargo-promoter` | **teammate** | read-only in the main, and the one mutation each may make is gated regardless |
| `mutating` | `terraform-engineer`, `helm-engineer`, `delivery-engineer`, `ticket-analyst` | **subagent** | they write files; two in parallel is the overwrite case |

No new metadata: the class that decides the mode is already in the agent.

## Which mode for which request

| Request shape | Mode | Reason |
|---------------|------|--------|
| One domain — "why is this pod crashing" | subagent | a team's coordination costs more than the question |
| `"X is down in <env>"` | **team**, 3–5 read-only members | the fan-out already in `routing-table.md` |
| Competing hypotheses | **team**, adversarial | sequential investigation anchors on the first plausible theory and stops looking |
| Review along several axes | **team**, one axis each | a single reviewer gravitates to one class of issue |
| Ticket delivery | subagents, sequential | ticket → worktree → change → PR is a chain, not a fan-out |
| Cross-repo change | subagents, ordered | an apply order exists; parallelism is the hazard, not the goal |
| Daily check | subagent | one agent, escalating only what it finds |

**Investigation fans out. Delivery runs as a chain.** That one line covers
most cases.

## Teams and subagents compose

A teammate may spawn subagents. Only teams do not nest:

- a teammate **cannot** spawn teammates — so write-chaining is structurally
  impossible, which prose alone never achieved
- a teammate's subagents run in the **foreground** only; a definition setting
  `background: true` is an error from a teammate
- the lead stays the lead for the session; leadership does not transfer

So an incident looks like: lead → three read-only teammates debating → each
using subagents for narrow sub-questions. Two levels, and no further.

## What changes about an agent when it arrives as a teammate

A definition does not behave identically in both modes. Each of these is a
real difference, not a detail:

| Field | As a subagent | As a teammate |
|-------|---------------|---------------|
| `skills` | preloaded | **not applied** — skills come from project/user settings |
| `permissionMode` | honoured | **ignored at spawn** — teammates inherit the lead's mode |
| `mcpServers` | ignored for a plugin agent | applied for a split-pane teammate; ignored in-process |
| the agent body | its instructions | **appended** to the default prompt in-process; **replaces** it in split panes |
| `tools` | honoured | honoured, plus messaging and task tools |

Two consequences worth stating plainly. A read-only agent cannot be made
read-only *by configuration* as a teammate — the class stays a declaration, so
its Boundaries remain the mechanism. And an agent whose instructions assume a
preloaded hub skill must still be able to find that skill itself.

## Team size and cost

Tokens scale linearly: every teammate is a separate session with its own
context. Start at **3–5**. Three focused members beat five scattered ones, and
past a point more members stop buying speed and start buying coordination.

Prefer teams for research, review and investigation. Prefer subagents for
anything that writes.

## Operating limits to brief the user on

- teams are **experimental**; in-process teammates do not survive `/resume`
- a task can be left stuck if a teammate fails to mark it complete
- split panes need tmux or iTerm2 — **not** available in Ghostty, Windows
  Terminal, or VS Code's integrated terminal, which fall back to the in-process
  agent panel
- teammate permission prompts surface in the **lead's** session, so pre-approve
  routine operations before fanning out or the lead becomes a prompt queue
- one team per session, and the lead cannot be changed

## Quality gates

Three hooks fire on team lifecycle and can hold the report contract to
account, rather than trusting it:

| Hook | Exit code 2 | Use for |
|------|-------------|---------|
| `TeammateIdle` | send feedback, keep it working | a finding with no named owner is an observation, not a hand-off |
| `TaskCompleted` | block completion, send feedback | "all clear" claimed while a check did not run |
| `TaskCreated` | block creation, send feedback | a mutating task with no environment stated |

These gate the team's own protocol, which is different from policing an
agent's commands — see `safety-limits.md` for why that distinction matters.
Not yet implemented here.
