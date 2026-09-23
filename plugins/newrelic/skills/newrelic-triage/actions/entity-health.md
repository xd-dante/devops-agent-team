# Action — Entity Health

Golden signals for one named service, or a small set. The follow-up when the
digest flags something and you want the shape of it.

## Step 1 — Find the entity

```bash
nr '{ actor { entitySearch(query: "name LIKE '"'"'%<service>%'"'"'") {
  results { entities { name entityType guid alertSeverity reporting } } } } }' \
| jq -r '.data.actor.entitySearch.results.entities[]
         | "\(.entityType)\t\(.alertSeverity)\t\(.name)\t\(.guid)"'
```

Several matches → ask which, rather than picking the first. Names collide
across environments, and diagnosing staging while the user means production
produces a confident wrong answer.

## Step 2 — The four signals, week over week

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT count(*) AS throughput,
          percentage(count(*), WHERE error IS true) AS errorRate,
          percentile(duration, 50, 95, 99) AS pct,
          apdex(duration, t: 0.5) AS apdex
   FROM Transaction WHERE appName = '"'"'<service>'"'"'
   SINCE 6 hours ago COMPARE WITH 1 week ago") { results } } } }' \
| jq '.data.actor.account.nrql.results'
```

| Signal | Reading |
|--------|---------|
| Throughput **down** | A silent service. Check upstream before assuming health |
| Throughput **up** with latency up | Load-driven — capacity, not a code regression |
| Error rate up, throughput flat | A code or dependency problem |
| p99 up, p50 flat | A tail problem: a slow dependency, lock contention, or GC |
| p50 and p99 both up | Systemic — the whole service is slower |

p50 moving with p99 tells a different story from p99 alone. Reporting only
p95 hides both.

## Step 3 — Where is the time going

```bash
# slowest transactions
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT percentile(duration, 95) FROM Transaction
   WHERE appName = '"'"'<service>'"'"' FACET name
   SINCE 6 hours ago LIMIT 10") { results } } } }' | jq '.data.actor.account.nrql.results'

# errors by class
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT count(*) FROM TransactionError
   WHERE appName = '"'"'<service>'"'"' FACET error.class, error.message
   SINCE 6 hours ago LIMIT 10") { results } } } }' | jq '.data.actor.account.nrql.results'

# external dependencies
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT average(duration), count(*) FROM Span
   WHERE appName = '"'"'<service>'"'"' AND span.kind = '"'"'client'"'"'
   FACET name SINCE 6 hours ago LIMIT 10") { results } } } }' | jq '.data.actor.account.nrql.results'
```

An error class concentrated in one transaction is a different fix from the
same rate spread across all of them. Say which it is.

## Step 4 — Correlate with a change

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "SELECT timestamp, revision, user FROM Deployment
   WHERE appName = '"'"'<service>'"'"' SINCE 3 days ago") { results } } } }' \
| jq -r '.data.actor.account.nrql.results[]? | "\(.timestamp)\t\(.revision)"'
```

Onset within ~30 minutes of a deploy is strong evidence. Onset with no deploy
points at a dependency, data volume, or infrastructure — and that is a
different owner.

## Step 5 — Report

```
Service:   <name> (<type>)   alertSeverity: <x>   reporting: <yes/no>
Window:    last 6h vs same window last week

throughput  <n>/min   (<±%>)
error rate  <n>%      (baseline <n>%)
p50 / p95 / p99  <a> / <b> / <c> ms   (baseline <a> / <b> / <c>)
apdex       <n>       (target <t>)

Shape:      <tail | systemic | load-driven | error-only>
Top error:  <class> ×<n> — concentrated in <transaction> | spread
Slowest:    <transaction> p95 <n>ms
Dependency: <name> avg <n>ms ×<n>
Change:     deploy <revision> at <time> — <within|outside> the onset window

Likely cause: <explanation, or ranked hypotheses>
Owner:        <agent> → <repo/file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Picking the first name match | Ask; names collide across environments |
| Reporting p95 alone | p50 vs p99 distinguishes tail from systemic |
| Reading a throughput drop as healthy | A silent service is a failure |
| Ignoring the deploy timeline | Onset near a deploy is the cheapest evidence there is |
| Reporting an error rate without its baseline | Some services always run at 2% |
| Guessing the cause from metrics alone | Route to the agent that can see the code or cluster |
