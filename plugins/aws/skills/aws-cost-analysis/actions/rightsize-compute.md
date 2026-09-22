# Action — Rightsize Compute

Instances, cluster nodes, and databases larger than the workload needs — or
commitments not being used.

## Step 1 — What the provider already recommends

```bash
aws ce get-rightsizing-recommendation --service AmazonEC2 \
  --query 'RightsizingRecommendations[].{Id:CurrentInstance.ResourceId,Action:RightsizingType,Savings:TerminateRecommendationDetail.EstimatedMonthlySavings}' --output table

aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT --lookback-period-in-days SIXTY_DAYS \
  --query 'SavingsPlansPurchaseRecommendation.SavingsPlansPurchaseRecommendationSummary'
```

Free, data-driven, and worth checking first — "no commitment coverage at all"
is a common and large finding.

## Step 2 — Verify against real utilisation

```bash
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=<id> \
  --start-time "$(date -u -v-14d +%Y-%m-%dT%H:%M:%S)" --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 86400 --statistics Average Maximum --output table
```

Fourteen days, **average and maximum**. Peaks matter as much as means.

On burstable classes check the credit balance before calling anything idle.

## Step 3 — Databases

Small instance classes are often already near the floor, so there is little
to reclaim by shrinking — and connection exhaustion is the more common
problem. Moving **up** one class is frequently the right answer, and a
connection proxy is usually not: it can cost more than the instance it fronts
and does not raise the connection ceiling.

## Step 4 — Cluster nodes

Node cost is driven by what pods **request**, not what they use:

```bash
kubectl describe node <node> | sed -n '/Allocated resources:/,/Events:/p'
```

So an oversized node pool is usually the symptom of oversized pod requests —
a chart change (`helm-agent`), not a pool change (`terraform-agent`). Say
which.

## Step 5 — Existing commitments

```bash
aws ce get-savings-plans-utilization --time-period Start=<start>,End=<end> --query 'Total'
aws ce get-reservation-utilization --time-period Start=<start>,End=<end> --query 'Total'
```

Underused commitments are a real loss. Report utilisation alongside any
purchase recommendation.

## Report

```
Account:   <id>   Period: <window>
Provider recommends: <n> actions, <amount>/mo; commitment <rate> → <amount>/mo
Verified:  <resource> avg <x>% peak <y>% over 14d → <keep | downsize | commit>
Databases: <at floor | size-up candidates>   credits: <exhausted?>
Nodes:     driver is <pod requests | pool sizing> → <owner>
Commitments: utilisation <x>%
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Acting on a recommendation without checking metrics | 14 days, average **and** maximum |
| Calling a burstable instance idle | Check the credit balance |
| Shrinking databases already at the floor | Little to reclaim |
| Proposing a connection proxy to save money | It can cost more than the instance |
| Resizing node pools for low utilisation | The driver is usually pod requests |
| Recommending a commitment without checking existing utilisation | Report both |
