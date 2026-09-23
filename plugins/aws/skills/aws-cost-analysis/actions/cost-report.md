# Action — Cost Report

Turn findings into a ranked, routable report. The deliverable.

## Step 1 — Rank by saving per unit of effort

Not by absolute saving. A one-filter change beating a migration worth twice
as much is the normal outcome.

## Step 2 — Every item carries the same fields

| Field | Why |
|-------|-----|
| Finding | What is costing money |
| Monthly | The figure, and how it was derived |
| Confidence | measured / estimated / inferred |
| Effort | low / medium / high |
| Risk | Including lost observability or resilience |
| Owner | Repo and agent that makes the change |

An item without an owner is not routable, so it does not count as delivered.

## Step 3 — Be honest about trade-offs

Inline, in the recommendation:

- cutting access logs reduces debuggability
- cheaper log destinations are harder to query
- removing a duplicate trail requires knowing what reads it
- downsizing a burstable instance can exhaust credits under load
- commitments are commitments — under-use is a real loss

## Step 4 — Three separate figures

```
Total spend:     <amount>/mo   (metric, pre/post tax)
Addressable:     <amount>/mo   (sum of recommendations)
Recommended now: <amount>/mo   (the subset to act on first)
```

Never blur them.

## Step 5 — Report

```
Cost Review — <account> / <period>
Metric: UnblendedCost (pre-tax)

Total: <amount>/mo        Addressable: <amount>/mo across <n> findings

Ranked recommendations
 1. <finding> — <amount>/mo | confidence <x> | effort low | risk <y>
    Owner: terraform-engineer → <repo>/<file>
    Action: <the specific change>

Verified clean
  - <checked and fine, briefly>

Not investigated
  - <out of scope, and why>

Assumptions
  - <period, lookback windows, estimate basis>

Nothing was mutated.
```

## Step 6 — Route the follow-up

Each accepted item becomes an infrastructure change:
`HANDOFF → terraform-engineer` with the repo and file named. Protected
environments need their own confirmation.

For tracking, `HANDOFF → ticket-analyst` — **one ticket per independently
actionable item**, not one omnibus ticket.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Ranking by absolute saving | Saving per unit of effort |
| Recommendations without an owner | Name the repo and agent |
| Presenting estimates as measurements | Label confidence per item |
| Hiding trade-offs | State them in the recommendation |
| Blurring total and addressable | Three separate figures |
| One omnibus ticket | One per actionable item |
