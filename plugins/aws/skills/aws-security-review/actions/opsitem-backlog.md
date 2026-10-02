# Action — Operations Backlog

Why there are so many open OpsCenter items, which are stale, and the exact
lists a human would approve to clear them.

## Step 1 — Count, per account and region

```bash
aws ssm get-ops-summary --filters Key=AWS:OpsItem.Status,Values=Open,Type=Equal \
  --aggregators AggregatorType=count,TypeName=AWS:OpsItem,AttributeName=Status
```

Run it in every account that has the integration enabled. The administrator
and the members can **each** mirror the same member findings.

## Step 2 — Find the generator

```bash
aws ssm get-service-setting --setting-id /ssm/opsdata/SecurityHub \
  --query 'ServiceSetting.[SettingValue,LastModifiedDate,LastModifiedUser,Status]'
aws events list-rules --query 'Rules[?ManagedBy!=`null`].[Name,ManagedBy,State]'
aws events list-targets-by-rule --rule <managed-rule-name>
```

- The integration setting decides which severities become items. A value
  that includes optional medium and low findings is usually where the volume
  comes from.
- Report the value, when it changed, and whether infrastructure code owns it
  (grep for the setting id across every infrastructure repo). It is often
  set by hand.
- Other item sources are small but real: alarm-driven rules, patch and
  instance events. Count each by `Source` and `CreatedBy`.

## Step 3 — Pull and join

```bash
aws ssm describe-ops-items --ops-item-filters Key=Status,Values=Open,Operator=Equal \
  --output json > ops-open.json

jq -r '.OpsItemSummaries[] | select(.Source=="Security Hub") |
  [.OpsItemId, .Severity, (.OperationalData["/aws/dedup"].Value|fromjson|.dedupString),
   .Title, .CreatedTime] | @tsv' ops-open.json > ops.tsv

awk -F'\t' 'NR==FNR{a[$1];next} !($3 in a)' active-ids.txt ops.tsv > stale.tsv
awk -F'\t' 'NR==FNR{a[$1];next}  ($3 in a)' active-ids.txt ops.tsv > live-backed.tsv
```

The dedup string is the source finding id. Use the `active-ids.txt` file
that `actions/findings-inventory.md` wrote **in the same account**.

Bucket both files by severity (1 critical … 4 low), by title with ids
stripped, and by created month. A bucket with one item per distinct
instance is churn from ephemeral compute.

## Step 4 — Prove staleness on a sample

"Not in the active set" can mean archived, purged, resolved or suppressed.
None of these need action, but check a sample spread across the list:

```bash
aws securityhub get-findings --filters '{"Id":[{"Value":"<id>","Comparison":"EQUALS"}]}' \
  --query 'Findings[].[RecordState,Workflow.Status]' --output text   # empty = purged
```

The filter accepts about 20 values per field, so batch the ids.

## Step 5 — Prepare the lists, do not act

| File | Contents | Use |
|------|----------|-----|
| `stale.tsv` | items whose finding is no longer active | approved bulk resolve |
| `live-backed.tsv` | items backed by an active finding | leave open until fixed |

Split `stale.tsv` by severity, so the approver can choose to release low and
medium first and review critical and high separately.

For the human or runner who executes an approved resolve, state:

- re-check each finding just before resolving
- add an operational-data note pointing at the tracking ticket
- log every id with a timestamp, so the run can be reverted
- rate-limit and run in parallel within API limits; a single-threaded CLI
  loop manages roughly 30 items per minute
- stop the inflow first (the integration setting), or the backlog refills

## Report

```
Open items: <account>: <n> (Security Hub <n>, other <n>)
Generator: <setting value> since <date> by <principal>; in code: <yes/no>
Stale: <n> (<%>) — by severity 1/2/3/4 — top buckets
Live-backed: <n> — by severity
Duplicated across administrator and member: <n>
Inflow: <items/day, recent month>
Prepared: stale.tsv (<rows>), live-backed.tsv (<rows>), pulled at <time>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Assuming items close when findings resolve | They never do. Every fix needs a resolve step afterwards |
| Joining items to another account's findings | Join within the same account |
| Recommending a bulk resolve before stopping inflow | Change the generator first, or say why not |
| Calling the backlog "N open problems" | Report stale vs live-backed |
| Running `update-ops-item` "to test" | Read-only. Prepare the list and route it |
