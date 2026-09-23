# Action — Alert Review

A periodic audit of the alerting itself, not of today's incidents. Answers:
**would we actually find out?**

Not part of a daily run — monthly, or after an incident nobody was paged for.

## Step 1 — Inventory

```bash
nr '{ actor { account(id: ACCOUNT) { alerts {
  policiesSearch { policies { id name incidentPreference } }
  nrqlConditionsSearch { nrqlConditions {
    id name type enabled policyId
    nrql { query }
    terms { threshold thresholdOccurrences thresholdDuration priority operator }
  } } } } } }' | tee /tmp/nr-alerts.json | jq '.data.actor.account.alerts | keys'
```

## Step 2 — The four failure modes worth finding

| Finding | How to spot it | Why it matters |
|---------|----------------|----------------|
| **Disabled conditions** | `enabled == false` | Someone silenced it during an incident and never turned it back on. The most common real gap |
| **Never-fired conditions** | No issue has ever referenced it | Either the threshold is unreachable, or the query returns nothing — both mean no coverage |
| **Critical service with no condition** | `observability.critical_services` minus the entities covered by conditions | The gap nobody notices until the outage |
| **Policy with no notification** | Policy has conditions but no channel/workflow | It fires into the void |

```bash
jq -r '.data.actor.account.alerts.nrqlConditionsSearch.nrqlConditions[]
       | select(.enabled == false) | "DISABLED\t\(.name)"' /tmp/nr-alerts.json
```

For never-fired, compare the condition list against issue history:

```bash
nr '{ actor { account(id: ACCOUNT) { aiIssues { issues(filter: {states: [CLOSED, ACTIVATED]}) {
  issues { title entityNames } nextCursor } } } } }' \
| jq -r '.data.actor.account.aiIssues.issues.issues[].title' | sort -u
```

A condition whose name never appears is a candidate — confirm by running its
own NRQL and checking it returns rows at all.

## Step 3 — Does the threshold match reality

For each condition on a critical service, run its own query over a
representative window and compare against the configured threshold:

```bash
nr '{ actor { account(id: ACCOUNT) { nrql(query:
  "<the condition NRQL> SINCE 7 days ago") { results } } } }' \
| jq '.data.actor.account.nrql.results'
```

Two failures to name:

- **Threshold above anything ever observed** → it cannot fire. Dead coverage
  that reads as coverage, which is worse than none
- **Threshold inside normal variance** → it fires constantly, gets muted, and
  takes real signal with it

Both are reported with the observed range next to the configured number.
"Threshold is wrong" without the numbers is not actionable.

## Step 4 — Report

```
Alert coverage — <account> (<id>, <region>)
Policies: <n>   Conditions: <n> (<n> disabled)

🔴 <n> critical services with no alert condition
   <service> — nothing covers it

🟠 <n> disabled conditions
   <name> — disabled, on policy <policy>

🟠 <n> conditions that have never fired
   <name> — threshold <x>, observed 7d range <min>–<max> (unreachable)

🟡 <n> likely noisy
   <name> — threshold <x>, normal variance reaches <y>

Owner: terraform-engineer if conditions are managed as code, otherwise the
console — say which, and do not change them here
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Auditing conditions without checking the thresholds | An unreachable threshold reads as coverage |
| Assuming a condition works because it exists | Check it has ever fired |
| Ignoring notification wiring | A firing policy with no channel is silent |
| Reporting "threshold is wrong" with no numbers | Give the configured value and the observed range |
| Running this daily | Monthly, or after a missed incident |
| Fixing it here | Read-only; route to whoever owns the config |
