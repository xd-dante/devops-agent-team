# Action — Observability and Transfer

Logs, metrics, trails, and data movement. Reliably the largest addressable
category, and the one where the obvious fix is wrong.

## Step 1 — Split ingestion from storage

```bash
aws ce get-cost-and-usage \
  --time-period Start=<start>,End=<end> --granularity MONTHLY --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["<logs service>"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --query 'ResultsByTime[0].Groups[].{Usage:Keys[0],Cost:Metrics.UnblendedCost.Amount}' --output table
```

Storage is typically a rounding error against ingestion. **Reducing retention
saves almost nothing.** The lever is what gets emitted.

## Step 2 — Find the loudest groups, then the emitter

```bash
aws logs describe-log-groups \
  --query 'reverse(sort_by(logGroups,&storedBytes))[:15].{Name:logGroupName,GB:storedBytes,Retention:retentionInDays}' --output table
```

Then find **who is emitting**, not just where it lands. A single service
account polling an API server hundreds of times a second can dominate a
control-plane audit log — and that is an application-behaviour fix, not a
logging-configuration one.

```bash
aws logs start-query --log-group-name <group> \
  --start-time $(( $(date +%s) - 3600 )) --end-time $(date +%s) \
  --query-string 'fields @timestamp | stats count(*) as calls by <identity-field> | sort calls desc | limit 20'
```

Keep the window tight — the query itself is billed per GB scanned.

A group with null retention keeps data forever. Worth flagging, but remember
step 1: it is rarely where the money is.

## Step 3 — Unfiltered exporters

```bash
aws cloudwatch list-metric-streams \
  --query 'Entries[].{Name:Name,State:State,Filters:IncludeFilters}' --output table
```

No include-filters means **everything**, continuously. A one-line fix with an
immediate effect, and easy to miss because nothing looks broken.

## Step 4 — Duplicate trails

```bash
aws cloudtrail describe-trails \
  --query 'trailList[].{Name:Name,Multi:IsMultiRegionTrail,Org:IsOrganizationTrail,Bucket:S3BucketName}' --output table
```

Two overlapping trails recording the same management events is pure
duplication. Confirm what reads each before recommending removal.

## Step 5 — Mesh and access logs

Full-verbosity access logging in a service mesh produces very large volumes.
The decision is a **trade-off, not a pure saving**: sampling or disabling it
in lower environments reduces debuggability. Say so in the recommendation.

## Step 6 — Flow log destination

```bash
aws ec2 describe-flow-logs \
  --query 'FlowLogs[].{Id:FlowLogId,Dest:LogDestinationType,Resource:ResourceId}' --output table
```

Delivery to a log service is charged at a vended rate; object storage is
materially cheaper. Query ergonomics get worse — mention it.

## Step 7 — NAT and egress: two charges, two fixes

```bash
aws ce get-cost-and-usage \
  --time-period Start=<start>,End=<end> --granularity MONTHLY --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["<vpc service>"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE --output table

for n in $(aws ec2 describe-nat-gateways --query 'NatGateways[?State==`available`].NatGatewayId' --output text); do
  echo "== $n"
  aws cloudwatch get-metric-statistics --namespace AWS/NATGateway --metric-name BytesOutToDestination \
    --dimensions Name=NatGatewayId,Value=$n \
    --start-time "$(date -u -v-7d +%Y-%m-%dT%H:%M:%S)" --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
    --period 86400 --statistics Sum --query 'Datapoints[].Sum' --output text
done
```

Hourly charges are about **how many gateways run**; data processing is about
**what flows through them**. Idle gateways are cheap to fix and usually not
where the money is.

Attribute the volume before recommending anything:

```bash
aws logs start-query --log-group-name <flow-log-group> \
  --start-time $(( $(date +%s) - 3600 )) --end-time $(date +%s) \
  --query-string 'fields dstaddr, bytes | stats sum(bytes) as total by dstaddr | sort total desc | limit 20'
```

Container image pulls and package registries are frequent causes — and the
fix is a **pull-through cache or a registry endpoint**, not a NAT change.
Check which services already have endpoints; traffic to those never traversed
NAT in the first place.

## Report

```
Account:    <id>   Period: <month>
Logs:       ingestion <amount> vs storage <amount>
Top groups: <group> <GB>/mo — emitter: <who>
Exporters:  <name> filters: <none|list> → <amount>/mo
Trails:     <n> recording management events — duplication <amount>/mo
Mesh logs:  <GB>/mo → <amount>/mo   (trade-off: debuggability)
Flow logs:  destination <x> → <amount>/mo if moved
NAT:        hourly <n> gateways <amount>/mo (idle: <list>) | data <TB>/mo <amount>/mo
Top egress: <destination/owner> <GB> — <image pulls | registry | vendor API>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Recommending shorter retention | Ingestion dwarfs storage — cut emission |
| Blaming the log group instead of the emitter | Find who is producing the volume |
| Assuming an exporter is filtered | Check; empty means everything |
| Removing a trail without checking consumers | Confirm what reads it |
| Presenting mesh-log cuts as free | They cost debuggability |
| Treating NAT as one charge | Hourly and data processing differ |
| Assuming applications drive egress volume | Attribute with flow logs |
| Leading with idle gateways | They are cheap; volume is the real number |
