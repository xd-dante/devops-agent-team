# Signal Triage

The point of a daily check is a **verdict**, not a data dump. This is how a
signal earns a place in the report.

## Severity

| Level | Means | Goes in the report |
|-------|-------|--------------------|
| 🔴 **Act now** | Customer-facing breakage, or a critical service degrading | Always, at the top, with the evidence |
| 🟠 **Look today** | A real regression that is not yet breaking anything | Always |
| 🟡 **Worth knowing** | Unusual but explainable, or a monitoring gap | One line each, grouped |
| ⚪ **Noise** | Known-flapping condition, expected batch spike, an issue already acknowledged | **Omit**, but say how many were suppressed and why |

Reporting noise at the same weight as breakage is how a daily check stops
being read.

## Default thresholds

Overridable per project via `observability.thresholds`:

| Signal | Default | Notes |
|--------|---------|-------|
| Error rate | > 1% of throughput | Compare against the service's own baseline before calling it |
| p95 latency | > 800 ms, or > 2× the 7-day median | The multiplier catches regressions an absolute number misses |
| Apdex | < 0.9 | Only where an apdex target is actually configured |
| Throughput drop | < 50% of same hour last week | A silent service is as bad as a failing one |
| Host/entity not reporting | `reporting = false` | Frequently a deploy or agent problem, not an outage |

An absolute threshold alone produces a report full of services that have
always been like that. Always pair it with a comparison.

## Compare against the same window

Week-over-week, same hour, not "the last hour vs the hour before":

```sql
SELECT count(*) FROM Transaction
  WHERE appName = '<service>'
  SINCE 1 hour ago COMPARE WITH 1 week ago
```

Weekday and hour-of-day dominate most application traffic. Comparing to the
previous hour flags every morning ramp as an incident.

## "All clear" has to mean something

Only report all clear when **every** check actually ran and returned data.

If a query failed, a region looked wrong, or an account came back empty, the
verdict is **"could not verify"** — never all clear. Those are different
findings, and conflating them is the one failure mode that makes this agent
worse than not running it.

```
✅  All clear — 6 checks ran, 0 act-now, 2 suppressed as known noise
✅  Could not verify — entity search returned a GraphQL error; issues and
    dashboards were clean
🚫  All clear
    (…when the issues query errored and was read as zero results)
```

## Recurrence is a finding

The same issue appearing every day is not one finding repeated — it is a
signal that a threshold is wrong or something is genuinely unfixed. Say how
many days it has been present; that is what turns it into a decision.

Memory helps here: if the `memory` plugin is enabled, an entry recording "this
condition flaps every deploy, ignore below 5 minutes" turns a daily
distraction into a one-line suppression. Offer to save it rather than
re-reporting it.

## Report shape

Short, verdict first, exceptions only:

```
Verdict:  🔴 act now | 🟠 look today | ✅ all clear | ⚠️ could not verify
Window:   <period>      Account: <name> (<id>, <region>)
Checks:   <n> ran, <n> failed

🔴 <what is broken> — <entity>
   evidence: <metric or issue, with the number>
   started:  <when>       owner route: <agent>

🟠 <regression> — <entity>
   evidence: <value> vs <baseline>

🟡 <n> worth knowing: <one line each>
⚪ <n> suppressed: <why>
```

If there is nothing above 🟡, the whole report is three lines. That is the
success case, not a lazy one.
