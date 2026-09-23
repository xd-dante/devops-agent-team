# Action — Daily Digest

The default run. **"Is anything actually wrong, and does it need me?"**
Answered in a few lines, in under a minute.

Optimised for being read every morning: verdict first, exceptions only,
nothing you already know.

## Step 0 — Prove the account

Per `standards/account-discovery.md`. Set up the `nr` helper, confirm the
region resolves to a real account. **Empty account list → stop and report**;
do not continue into checks that will all look clean.

## Step 1 — Open issues

```bash
nr '{ actor { account(id: ACCOUNT) { aiIssues {
  issues(filter: {states: [ACTIVATED]}) {
    issues { issueId title priority state entityNames createdAt }
    nextCursor } } } } }' \
| tee /tmp/nr-issues.json \
| jq -r '.data.actor.account.aiIssues.issues.issues[]
         | "\(.priority)\t\(.title)\t\(.entityNames|join(","))"' | sort
```

Check `.errors` first. Follow `nextCursor` until empty.

`CRITICAL` priority and anything on a service listed in
`observability.critical_services` is a 🔴 candidate — subject to the noise
rules in `standards/signal-triage.md`.

## Step 2 — Entity health, in one sweep

```bash
nr '{ actor { entitySearch(query: "alertSeverity IS NOT NULL") {
  count results { entities { name entityType alertSeverity reporting } } } } }' \
| jq -r '.data.actor.entitySearch.results.entities[]
         | select(.alertSeverity != "NOT_ALERTING" or .reporting == false)
         | "\(.alertSeverity)\t\(if .reporting then "reporting" else "NOT REPORTING" end)\t\(.name)"'
```

`reporting = false` is easy to miss and often the more serious finding: an
entity that stopped sending data raises no alerts at all. A service that
went silent looks identical to a service that is fine.

## Step 3 — Golden signals on the critical services only

One NRQL pass, week-over-week so normal daily shape does not register:

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT count(*) AS throughput,
          percentage(count(*), WHERE error IS true) AS errorRate,
          percentile(duration, 95) AS p95
   FROM Transaction FACET appName
   SINCE 1 hour ago COMPARE WITH 1 week ago")
  { results } } } }' | jq '.data.actor.account.nrql.results'
```

Apply the thresholds and the comparison rule from
`standards/signal-triage.md`. A number without its baseline is not a
finding.

## Step 4 — Did the dashboards break

A cheap staleness check — a dashboard whose widgets return no data is a
monitoring failure that hides everything behind it:

```bash
nr '{ actor { entitySearch(query: "type = '"'"'DASHBOARD'"'"'") {
  count results { entities { name guid } } } } }' \
| jq -r '.data.actor.entitySearch.results.entities[].name'
```

Only spot-check dashboards listed in `observability.dashboards`. For a full
pass use `actions/dashboard-review.md` — not part of a daily run.

## Step 5 — Anything deployed since yesterday

Correlation beats investigation. If a regression started at a deploy, say so:

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT timestamp, appName, revision FROM Deployment
   SINCE 1 day ago LIMIT 50") { results } } } }' \
| jq -r '.data.actor.account.nrql.results[]? | "\(.timestamp)\t\(.appName)\t\(.revision)"'
```

No `Deployment` events is normal where deploy markers are not wired up — note
it once, do not treat it as a finding.

## Step 6 — Report

Per `standards/signal-triage.md`. Nothing above 🟡 → three lines and stop.

```
Verdict:  ✅ all clear
Window:   last 1h vs same hour last week   Account: <name> (<id>, US)
Checks:   5 ran, 0 failed  ·  ⚪ 2 suppressed (known deploy flap on <svc>)
```

With something real:

```
Verdict:  🔴 act now
Window:   last 1h vs same hour last week   Account: <name> (<id>, US)
Checks:   5 ran, 0 failed

🔴 checkout-api error rate 4.2% (baseline 0.3%) — 14× normal
   started 06:40Z, 20m after deploy <revision>
   open issue: "Error rate elevated" (CRITICAL, 38m)
   → route: kubernetes-investigator for pod-level cause, then the deploy

🟠 search-api p95 1.9s (baseline 620ms)
   no deploy; began 05:10Z

🟡 2 worth knowing: batch-worker not reporting since 02:00Z (expected —
   nightly window); 1 dashboard has a widget with no data for 3 days
```

Every 🔴 and 🟠 names the agent that owns the next step. A finding with no
route is an observation, not a hand-off.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reporting all clear when a query errored | Check `.errors`; the verdict is "could not verify" |
| Listing every open issue | Suppress known noise, count the suppressions |
| Comparing to the previous hour | Same hour last week — daily shape dominates |
| Ignoring `reporting = false` | A silent entity raises no alerts and looks healthy |
| An absolute threshold with no baseline | Pair every number with its comparison |
| A wall of metrics | Verdict first, exceptions only; three lines is a good day |
| Not paginating issues | `nextCursor` until empty, or problems are truncated away |
| Findings with no owner | Name the agent that takes the next step |
