# Action — NRQL Query

A specific question, asked directly. The escape hatch from the canned checks:
"how many 500s did checkout throw overnight", "which endpoint got slower
after the release".

## Step 1 — Pin the question

Before writing NRQL, fix four things:

| | Why |
|---|---|
| **Event type** | `Transaction`, `TransactionError`, `Span`, `Log`, `Metric`, a custom event — the wrong one returns nothing and looks like an answer |
| **Window** | Always `SINCE`. Unbounded queries are slow and billed |
| **Filter** | Which service, which environment |
| **Shape** | A number, a breakdown (`FACET`), or a trend (`TIMESERIES`) |

## Step 2 — Confirm the data exists before trusting a zero

```bash
# does this event type have anything at all?
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT count(*) FROM <EventType> SINCE 1 day ago") { results } } } }' \
| jq '.data.actor.account.nrql.results'

# what attributes does it actually carry?
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT keyset() FROM <EventType> SINCE 1 day ago") { results } } } }' \
| jq '.data.actor.account.nrql.results'
```

`keyset()` is the fastest way to stop guessing attribute names. A filter on
an attribute that does not exist returns zero rows with no error — which
reads as "nothing happened".

## Step 3 — Build it up

```sql
-- a number
SELECT count(*) FROM TransactionError
 WHERE appName = '<service>' AND error.class LIKE '%Timeout%'
 SINCE 12 hours ago

-- a breakdown
SELECT count(*) FROM Transaction
 WHERE appName = '<service>' AND httpResponseCode >= '500'
 FACET httpResponseCode, name SINCE 12 hours ago LIMIT 20

-- a trend
SELECT percentile(duration, 95) FROM Transaction
 WHERE appName = '<service>' TIMESERIES 15 minutes SINCE 6 hours ago

-- before and after a release
SELECT percentile(duration, 95), percentage(count(*), WHERE error IS true)
 FROM Transaction WHERE appName = '<service>'
 SINCE 2 hours ago COMPARE WITH 1 day ago
```

Useful and easy to forget:

| Clause | Use |
|--------|-----|
| `COMPARE WITH` | Any "did it get worse" question |
| `FACET ... LIMIT n` | Breakdowns; the default limit is small and truncates silently |
| `keyset()` | Discover attributes rather than guessing |
| `uniqueCount()` | Distinct users or hosts affected — turns a rate into an impact |
| `percentage(count(*), WHERE ...)` | Rates without two queries |

## Step 4 — Sanity-check the answer

Before reporting a number, ask whether it can be true:

- An error count higher than the throughput means the filter is wrong
- An exact zero on a busy service usually means a typo'd attribute
- A p95 in microseconds or hours means the wrong unit or event type

A confidently wrong number is the main risk of this action. Cross-check
anything surprising with a second query shaped differently.

## Step 5 — Report

```
Question:  <the question, restated>
Query:     <the NRQL, verbatim>
Window:    <period>            Account: <name> (<id>, <region>)

Answer:    <the number or table>
Sanity:    <what you checked to believe it>
Caveat:    <sampling, missing instrumentation, partial window>
```

Give the NRQL. It makes the answer reproducible and lets the user spot a
wrong filter immediately.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Trusting a zero | Confirm the event type has data, and check attributes with `keyset()` |
| Guessing attribute names | `keyset()` |
| No `SINCE` | Slow and billed |
| Forgetting `LIMIT` on a `FACET` | The default truncates without saying so |
| Reporting a number with no query | Unreproducible, and a wrong filter stays hidden |
| Not sanity-checking a surprise | Errors above throughput means the filter is wrong |
