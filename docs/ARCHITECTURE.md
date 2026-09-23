# Architecture

## The four layers

```
agents/<name>.agent.md           WHO   — role, skill list, handoffs, boundaries
skills/<hub>/SKILL.md            WHICH — router: capability → action
skills/<hub>/actions/<flow>.md   HOW   — one flow: steps, report, mistakes
skills/<hub>/standards/<rule>.md RULES — always-applies rules + checklist
```

Why split this way:

| Layer | Answers | Loaded |
|-------|---------|--------|
| Agent | "am I the right one, and what may I do?" | on dispatch |
| Hub skill | "which of my flows is this?" | once per task |
| Action | "what are the steps, and what is the output?" | one per task |
| Standards | "what is always true here?" | with the action |

An agent never loads its whole domain. It loads the router, picks one action,
and loads that action plus the standards. Token cost tracks the task, not the
size of the domain.

## Why one agent per domain

A general agent has one set of boundaries. A domain agent can refuse the
specific things that are dangerous in *its* domain:

- the cluster agent treats `exec` and `port-forward` as mutating
- the Terraform agent refuses untargeted applies
- the cost agent refuses to present an estimate as a measurement
- the Argo CD agent refuses to edit a Terraform-owned CRD in place

Those rules contradict each other's defaults. They cannot all live in one
prompt without becoming advisory noise — so they live in separate agents with
separate `Never` lists.

## Routing

`plugins/devops/skills/orchestrate/standards/routing-table.md`
maps a domain signal to an agent, and — more usefully — holds the
**disambiguation rules** for requests that genuinely look like two domains:

| Looks like both | Goes to | Because |
|-----------------|---------|---------|
| "pod unhealthy" + "app shows Degraded" | cluster agent first | pod evidence explains the app status; the reverse rarely holds |
| "running the wrong version" | promotion agent | version movement is a promotion concern before a sync or chart one |
| "synced but nothing changed" | GitOps agent | usually a pinned target revision |
| "the database is slow" | investigator | engine behaviour |
| "the database is expensive" | cost agent | money questions always go to cost |

A new agent that is not added to that table never gets dispatched. The table
is the contract, not the agent's own description.

## Briefing

Specialists start with **no conversation history**, so every brief is
self-contained. The delegation protocol requires:

objective · scope boundary · environment + cloud profile · absolute paths ·
ticket id · facts already established · required output shape

"See above" is meaningless to a cold agent. This is the single most common
way multi-agent setups produce confident nonsense.

## Handoffs

```
HANDOFF → <agent>
objective: <one sentence, outcome-shaped>
context:   <facts already established, so it does not re-derive them>
scope:     <what it must not touch>
output:    <what to return>
```

Two routes, deliberately asymmetric:

- **Mutations route through the orchestrator.** It owns sequencing and
  approval. Agents cannot chain changes between themselves.
- **Read-only questions may go peer to peer**, one hop deep, and must be
  reported.

Reads flow sideways; writes do not. That is the loop-prevention design —
there is no depth limit to enforce for writes because writes never chain.

## Verification

A specialist's report is evidence, not a verdict. Before it reaches the user
the orchestrator checks:

- does the stated evidence actually support the conclusion?
- did the agent stay inside its boundaries — did a read-only agent mutate?
- are paths, PR numbers and resource names real? (spot-check one)
- if two specialists disagree, say so and name the cheapest settling check —
  never average them into a soft answer

## Gating

Mutating actions open with a precondition checklist and stop if any item is
unticked. The pattern:

```markdown
## Gate — all required
- [ ] User approved **this** target and **this** run
- [ ] The diff or plan was shown first
- [ ] Environment named; protected environments confirmed separately
Any box unticked → 🛑 STOP.
```

This is why read-only and mutating flows live in separate action files: the
gate is unavoidable rather than a paragraph an agent can skim past.

## Reporting

One consolidated report per task, in a fixed shape: task, routed-to,
environment, findings with evidence, root cause, done, **not done**, next.

"Not done" is mandatory when non-empty. Blocked and skipped work gets stated,
not quietly dropped — scaling the work down is the user's decision.

## What this is not

- Not tested software. These are structured prompts.
- Not a scheduler or a daemon. Agents run when dispatched.
- Not a credential store. Nothing here holds secrets; agents use whatever
  your shell is already authenticated with.
- Not org-specific. Anything site-specific is configured or discovered —
  see [CONFIGURATION.md](CONFIGURATION.md).
