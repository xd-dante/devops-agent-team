# Read-Only Rules

## The rule

**This agent reads. It does not change monitoring state.**

Its output is a report. The value of a daily check is that it is trustworthy,
and an agent that also silences things cannot be trusted to tell you what is
wrong.

## Allowed

Any NerdGraph **query**: issues, entities, alert policies and conditions,
dashboards, NRQL, deployment markers, SLO status.

## Forbidden

Every NerdGraph **mutation**, including:

- `aiIssues...Ack` / `Resolve` / `Unack` — acknowledging or closing an issue
- `alertsMutingRule...` — muting is how a real alert gets lost
- `alertsPolicy...` / `alertsNrqlCondition...Create|Update|Delete`
- `dashboard...Create|Update|Delete`
- `entityTag...` / anything touching workloads or notification channels
- Any API key creation or rotation

Acknowledging an issue looks harmless and is not: it removes the signal from
somebody else's queue and records your name against a decision you did not
make.

## Ask first

If the user explicitly asks to ack, mute, or change a condition, that is a
different job:

1. Say which mutation it needs and what it will suppress
2. Name the blast radius — which conditions, which entities, for how long
3. Get approval for **that** change, then hand over the exact mutation for
   them to run

Never bundle a mutation into a triage run.

## Data handling

- Report **counts and names**, not raw event payloads. Logs and traces can
  carry customer data
- Never paste a full log line into a report or a ticket without checking it
  first
- The user key is read from the environment. Never print it, never write it
  to a file, never put it in a config that gets committed

## Query cost

NRQL over long windows across high-volume event types is billed and slow.
Scope every query with `SINCE`, and prefer a narrow window plus a
comparison over one wide scan.

## Red flags — STOP

- About to run any mutation → recommend it instead
- About to report "all clear" from a query you did not check for `errors`
- About to report on an account list that came back empty → wrong region or
  key; stop and say so
- About to paste raw log output into a report → summarise instead
