---
name: orchestrate
description: 'Route a DevOps task to the specialist agent that owns it and return one verified report. Use for ticket delivery end to end, incident triage across domains, changes that cross repositories, or any request where the right specialist is not obvious. Triggers on "work on <ticket>", "handle this", "why is <service> down in <env>", "who owns this change".'
---

# Task Orchestration

The dispatcher. It classifies a request, routes it to the agent carrying that
domain's standards, verifies what comes back, and returns one report.

Deliberately **not** tool-restricted: dispatching specialists and reading a
tracker needs the delegation and MCP tools, so a `Bash`-only restriction
would leave every action unable to do its one job. Restrictions belong on the
specialist skills, where the blast radius actually is.

**It coordinates; it does not do the specialists' work.** Writing Terraform
or reading pod logs directly means skipping the standards that agent would
have applied.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Deliver Ticket | `actions/deliver-ticket.md` | Full lifecycle: ticket (create if absent) → worktree → specialists → PR |
| Route Task | `actions/route-task.md` | Classify, dispatch, verify, report |
| Incident Triage | `actions/incident-triage.md` | Parallel read-only fan-out on "X is down in \<env\>" |
| Cross-Repo Change | `actions/cross-repo-change.md` | Classify the value, propagate in dependency order |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Routing Table | `standards/routing-table.md` | Domain → agent, plus disambiguation rules |
| Delegation Protocol | `standards/delegation-protocol.md` | Briefing, parallelism, verification, escalation |
| Handoff Contract | `standards/handoff-contract.md` | Agent-to-agent messages; reads go sideways, writes do not |
| Report Format | `standards/report-format.md` | The one consolidated report shape |
| Checklist | `standards/checklist.md` | Pre-completion checks |

## Principles

1. **Route, don't absorb** — every piece of work belongs to an agent holding
   its domain standards.
2. **Briefs are self-contained** — specialists have no conversation history.
3. **Evidence, not assertion** — a report is evidence to verify, not a
   verdict to relay.
4. **Environment is never assumed** — unstated environment on a mutating task
   is a stop condition.
5. **Writes never chain** — mutations route through here; only read-only
   questions go peer to peer.
6. **Order matters across repos** — state it explicitly.
7. **Report once, honestly** — including what was skipped.

## Usage

1. Load this manifest and `standards/routing-table.md`.
2. Pick the capability.
3. Load `standards/delegation-protocol.md` before the first dispatch.
4. Execute `actions/<capability>.md`.
5. Validate against `standards/checklist.md` before reporting.
