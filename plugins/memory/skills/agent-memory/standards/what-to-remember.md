# What to Remember

## Types

| Type | Holds | Example shape |
|------|-------|---------------|
| `preference` | How the user wants work done | "Never untargeted applies in the shared state" |
| `convention` | An organisational rule not visible in the code | "PRs target `develop` in the chart repos" |
| `environment` | Site facts that cost time to rediscover | "These three environments share one cloud account" |
| `incident` | What broke, the real cause, and the tell | "Promotion step silently skipped — expression was task-scoped" |
| `reference` | Where something lives | "Dashboards are in <tool>, board id <n>" |

## Worth remembering

- A correction the user made to how you worked — especially a repeated one
- A non-obvious site fact you had to dig for (which branch, which account,
  which of two repos owns a resource)
- A failure mode with a **silent** signature — these are the expensive ones
- A decision and its reasoning, particularly a "we evaluated this and said
  no", so it is not re-proposed
- Where something lives that is not guessable

## Not worth remembering

| Do not store | Because |
|--------------|---------|
| Anything the code already says | It will go stale and then mislead |
| Anything git history already says | Same |
| A one-off answer with no future bearing | Noise crowds out signal |
| Task state ("currently on step 3") | That is conversation, not memory |
| A secret, token, or credential value | Memory is not a credential store |
| A restatement of a rule already in this toolkit | Improve the rule instead |

If the user asks you to remember something in the "not worth it" column, ask
what was non-obvious about it and store **that** instead.

## Scope

| Store as | When the fact is |
|----------|------------------|
| `project` | True of this codebase or repo only |
| `global` | True of how the user works, everywhere |

When unsure, project scope. A wrongly-global entry misfires in every other
repo, which is worse than one that simply does not apply here.

## Staleness

An entry records what was true when written. Before acting on one:

- if it names a file, function, branch, or flag — **verify it still exists**
- if reality disagrees with the entry, reality wins; then correct the entry
  (`actions/forget.md`)

Silently working around a wrong entry leaves it to mislead the next session.
