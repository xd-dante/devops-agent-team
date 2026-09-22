# Writing an Agent

Adding a domain means four files and one table row.

## 1. Plugin manifest

`plugins/<domain>/.claude-plugin/plugin.json`

```json
{
  "name": "<domain>",
  "description": "<one line>",
  "version": "1.0.0"
}
```

## 2. The agent

`plugins/<domain>/agents/<domain>.agent.md`

```markdown
---
name: <domain>-agent
description: <What it owns, in one or two sentences. Say PROACTIVELY and the
  trigger conditions. Say read-only explicitly if it is — the orchestrator
  reads this to decide whether a mutation may be routed here.>
---

<Two or three lines: what you own, and the one mental model that makes the
domain make sense.>

## Skills

| When the ask is… | Load |
|------------------|------|
| <trigger> | `actions/<flow>.md` |

Standards: `standards/<rule>.md` — read before acting.

## Discovery

<How to learn the environment at runtime. Config first, probe second, ask
third. Never hardcode a hostname, account or repo name.>

## Handoffs

| Finding | Hand to |
|---------|---------|
| <out-of-domain finding> | `<other>-agent` |

## Boundaries

- ✅ **Always:** …
- ⚠️ **Ask first:** …
- 🚫 **Never:** …
```

Keep `Boundaries` to the rules that change behaviour. Twenty bullets nobody
reads is worse than ten that bite.

## 3. The hub skill

`plugins/<domain>/skills/<hub>/SKILL.md` — a router, not a manual.

```markdown
---
name: <hub>
description: <When to use this skill. The harness matches on this.>
allowed-tools: Bash
---

# <Hub>

<Two lines of what this covers.>

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| <name> | `actions/<flow>.md` | <one line> |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| <name> | `standards/<rule>.md` | <one line> |

## Principles

1. **<Short rule>** — <one line of why>

## Usage

1. Load this manifest and `standards/<the main rule>.md`
2. Execute the capability's action file
3. Validate against `standards/checklist.md`
```

Target 60–80 lines. If it is longer, content belongs in an action.

## 4. Actions

`plugins/<domain>/skills/<hub>/actions/<flow>.md` — one flow each.

```markdown
# Action — <Name>

<One line: when this runs.>

## Gate — all required          ← mutating actions only
- [ ] <precondition>
Any box unticked → 🛑 STOP.

## Step 1 — <name>

```bash
<the actual command>
```

<What the output means. Tables beat paragraphs.>

## Report

```
<fixed output shape the agent must fill in>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| <the wrong move> | <the right one> |
```

Target 50–80 lines. Every action ends with a report shape and a mistakes
table — the mistakes table is where the real operational knowledge lives.

## 5. Standards

`standards/<rule>.md` holds rules, not procedure. Every hub skill also gets a
`standards/checklist.md` the agent validates against before reporting.

## 6. Register it — two places

**Marketplace** — `.claude-plugin/marketplace.json`:

```json
{
  "name": "<domain>",
  "description": "<one line>",
  "version": "1.0.0",
  "source": "./plugins/<domain>",
  "category": "development"
}
```

**Routing table** —
`plugins/orchestrator/skills/task-orchestration/standards/routing-table.md`.

> An agent absent from the routing table is never dispatched. This is the
> step people forget.

Add a disambiguation row too if your domain overlaps an existing one. That
row is usually more valuable than the agent itself.

## House style

- **Tables over prose.** They are read more reliably and cost fewer tokens.
- **One good/bad pair** per agent, showing the failure the domain actually
  produces. Not three.
- **Name consequences, not vibes.** "Auto-sync is off, so merging deploys
  nothing" beats "be careful with syncing".
- **No org-specific values.** No hostnames, account ids, cluster names,
  internal repo names, ticket ids, or figures from a real bill. Configure or
  discover — see [CONFIGURATION.md](CONFIGURATION.md).
- **Write the failure mode down.** A rule with its consequence attached gets
  followed; a bare instruction gets rationalised away.
