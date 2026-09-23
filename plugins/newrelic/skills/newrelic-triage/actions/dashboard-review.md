# Action — Dashboard Review

Are the dashboards still telling the truth? A dashboard with dead widgets is
worse than no dashboard: it is actively reassuring.

Periodic, not daily. Run it after a rename, a migration, or when someone says
"the graph looks empty".

## Step 1 — Inventory

```bash
nr '{ actor { entitySearch(query: "type = '"'"'DASHBOARD'"'"'") {
  count results { entities { name guid } } } } }' \
| jq -r '.data.actor.entitySearch.results.entities[] | "\(.guid)\t\(.name)"'
```

## Step 2 — Pull the widget queries

```bash
nr '{ actor { entity(guid: "<GUID>") { ... on DashboardEntity {
  name
  pages { name widgets {
    title
    rawConfiguration
  } } } } } }' > /tmp/nr-dash.json

jq -r '.. | .rawConfiguration? // empty | .nrqlQueries[]? .query' /tmp/nr-dash.json
```

`rawConfiguration` holds the widget definition; NRQL widgets carry
`nrqlQueries[].query`. Widgets of other types have no query and are skipped —
say how many were skipped rather than counting them as healthy.

## Step 3 — Run each query and classify the result

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query: "<widget query>") { results } } } }' \
| jq '{errors: .errors, rows: (.data.actor.account.nrql.results | length)}'
```

| Result | Meaning | Severity |
|--------|---------|----------|
| `errors` non-null | Invalid NRQL — a renamed attribute or event type | 🔴 broken |
| 0 rows, over a window that should have data | Filters a thing that no longer exists | 🔴 misleading |
| 0 rows, but the entity genuinely idle | Correct and empty | ⚪ fine |
| Rows returned | Working | ⚪ fine |

The distinction between the last three matters. Widen the window before
calling a widget dead:

```bash
# if 1 hour is empty, does 7 days have anything?
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "<widget query with SINCE 7 days ago>") { results } } } }' \
| jq '.data.actor.account.nrql.results | length'
```

Empty at one hour but populated over seven days = the widget works and the
thing is idle. Empty at both = broken.

## Step 4 — Look for what is missing

A dashboard can be entirely healthy and still not cover a critical service.
Compare the services referenced across all widget queries against
`observability.critical_services`:

```bash
jq -r '.. | .nrqlQueries[]? .query' /tmp/nr-dash.json \
| grep -oE "appName *= *'[^']+'" | sort -u
```

A critical service that appears in no dashboard is a 🟠 finding.

## Step 5 — Report

```
Dashboards: <n>   Widgets checked: <n>   Skipped (non-NRQL): <n>

🔴 <n> broken widgets
   <dashboard> › <page> › <widget>
   error: <verbatim NRQL error>

🔴 <n> misleading widgets (no data at 1h or 7d)
   <dashboard> › <widget> — filters <attribute> which returns nothing

🟠 <n> critical services on no dashboard
   <service>

⚪ <n> empty but correct (entity idle)

Owner: whoever owns the dashboard definitions — as code if they are managed
that way, otherwise the console. Read-only here.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Calling an empty widget broken | Widen to 7 days first; idle is not broken |
| Counting non-NRQL widgets as healthy | Report them as skipped |
| Only checking widgets render | A widget can render an empty chart cleanly |
| Missing absent coverage | Compare against the critical-service list |
| Running it daily | It is a periodic audit; the digest spot-checks instead |
| Fixing a query here | Read-only; route it |
