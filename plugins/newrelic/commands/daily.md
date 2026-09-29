---
description: Daily observability check — report only what needs attention, and who owns it
argument-hint: "[hours] (default 1)"
---

# Daily observability check

Four MCP queries, aggregated **server-side** so the wire carries tens of rows
instead of thousands of raw incidents. Run them, grade the result, name an
owner. Do not fetch raw incidents and group them yourself.

## Step 1 — Resolve configuration

From `.devops-agents.yml` (walk up from cwd), `observability:`:

| Key | Use |
|-----|-----|
| `region` | `US` or `EU`. A wrong region returns an **empty account, not an error** |
| `accounts` | alias → id. The alias starting `prod` is production |
| `suppress` | alert-condition names that are known noise |
| `thresholds.error_rate_pct`, `thresholds.p95_latency_ms` | regression gates |

Confirm the accounts exist with `list_available_new_relic_accounts` before any
check. An empty or unexpected list is a **stop condition** — every subsequent
check would come back clean.

If the MCP server is unauthenticated, say so and stop. Do not report a partial
run as a clean one. The OAuth access token is short-lived, so this happens.

## Step 2 — Incidents, grouped in the query

Per account, via `execute_nrql_query`. **`NrAiIncident`, not
`list_recent_issues`** — issues *group* incidents and under-report badly; on
one estate 10 issues concealed 241 incidents, including a condition firing on
100 entities.

```sql
SELECT uniqueCount(incidentId) AS incidents,
       uniqueCount(entity.name) AS entities,
       latest(priority) AS priority,
       earliest(timestamp) AS firstSeen
FROM NrAiIncident
WHERE event = 'open'
  AND conditionName NOT LIKE '%<each suppress entry>%'
FACET conditionName
SINCE 24 hours ago LIMIT 100
```

Then count what suppression removed, so it stays visible rather than silently
hiding a regression:

```sql
SELECT uniqueCount(incidentId) AS suppressed
FROM NrAiIncident
WHERE event = 'open'
  AND (conditionName LIKE '%<entry>%' OR conditionName LIKE '%<entry>%')
SINCE 24 hours ago
```

`FACET conditionName, account.id` works here if you prefer one cross-account
query — `account.id` is populated on `NrAiIncident`. Do **not** facet on
`tags.Environment`: it is unset on most conditions.

## Step 3 — Golden signals with their baseline

One query per account. `COMPARE WITH` returns `current` and `previous` rows in
the same response, so the baseline costs no extra call:

```sql
SELECT count(*) AS thr,
       percentage(count(*), WHERE error IS true) AS err,
       percentile(duration, 95) AS p95
FROM Transaction FACET appName
SINCE <hours> hours ago COMPARE WITH 1 week ago LIMIT 100
```

Query **per account**. `account.id` comes back NULL on `Transaction` facets, so
a cross-account version returns no regressions at all rather than unattributed
ones — which reads as "nothing wrong".

Two shapes to expect: `p95` is a dict (`{"95": 0.47}`), and duration may be in
**seconds** — normalise before comparing to a millisecond threshold.

Flag only against the baseline:

| Signal | Flag when |
|--------|-----------|
| error rate | `>= error_rate_pct` **and** more than 2× baseline |
| p95 | `>= p95_latency_ms` **and** more than 1.5× baseline |
| throughput | baseline ≥ 100 **and** current < half baseline |
| **went silent** | app has a `previous` row and **no `current` row** |

That last one replaces an entity-reporting check, which no MCP tool can
express. It catches a service that stopped reporting this week; it will
**not** catch one silent longer than the baseline window. Say so rather than
implying full coverage.

## Step 4 — Grade

- **🔴 act now** — anything in the production account: a non-chronic critical, or a regression
- **🟠 needs attention** — non-prod critical, or a non-prod regression
- **🟡 worth knowing** — everything else
- **⚠️ could not verify** — any query errored or the server was unauthenticated. **Never "all clear".**

`firstSeen` older than ~24h is **chronic**: not an incident, a threshold to
fix. Say that, and route it to whoever owns the alert policy.

Collapse non-production findings into counts by tier — `"11 critical
condition(s), 53 incidents: <top 3> …"`. List production individually. A
28-line digest does not get read, which defeats the purpose.

## Step 5 — Route

| Finding | Owner |
|---------|-------|
| node memory, pod not ready, restarts, capacity | `kubernetes-investigator` |
| error-rate or throughput break on a service | `kubernetes-investigator`, then the deploy |
| went silent | whoever owns that service's delivery |
| managed database, network path, IAM denial | `aws-investigator` |
| chronic condition | not an incident — the alert-policy owner |

## Step 6 — Report

Verdict first, exceptions only, then at most three lines of judgement: what
changed since yesterday, what is chronic and should be fixed rather than
watched, and the one thing worth doing first.

```
Verdict:  🔴 act now
Window:   incidents 24h · signals 1h vs same window last week · EU
Checks:   4 ran, 0 failed  ·  ⚪ 44 incidents suppressed as known noise

🔴 [prod] container-prod-high-cpu — 12 incidents; 4 entities; oldest 23h
🟠 [nonprod] core-worker: errors 91.59% (base 0.08%)
🟡 [nonprod] 9 warning-level condition(s), 30 incidents: <top 3> …
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `list_recent_issues` for the digest | Issues group incidents — use `NrAiIncident` |
| Fetching raw incidents and grouping them | `FACET` in the query; that is the whole point |
| Cross-account golden signals | `account.id` is NULL on `Transaction` — per account |
| `FACET tags.Environment` | Unset on most conditions; facet `account.id` |
| Comparing `p95` straight to the threshold | It is a dict, and often in seconds |
| "All clear" after a failed query | Could not verify |
| Relaying chronic noise daily | Name it chronic, propose the threshold change |
| A 28-line digest | Collapse non-prod to counts; prod individually |
| Findings with no owner | Name the agent that takes the next step |
