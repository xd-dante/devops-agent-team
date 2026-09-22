# Action — Cost Breakdown

Where the money goes. Always first.

## Step 1 — Identity and period

```bash
aws sts get-caller-identity --query 'Account' --output text
```

Fix the period explicitly. Cost-explorer calls are **billed per request**, so
plan the query set rather than exploring interactively.

## Step 2 — Total by month

```bash
aws ce get-cost-and-usage \
  --time-period Start=<YYYY-MM-DD>,End=<YYYY-MM-DD> \
  --granularity MONTHLY --metrics UnblendedCost \
  --query 'ResultsByTime[].{Period:TimePeriod.Start,Cost:Total.UnblendedCost.Amount}' --output table
```

`UnblendedCost` excludes tax. **Say which metric you used** and whether the
figure is pre- or post-tax — the two get compared carelessly.

## Step 3 — By service, top ten

```bash
aws ce get-cost-and-usage \
  --time-period Start=<start>,End=<end> --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[].{Service:Keys[0],Cost:Metrics.UnblendedCost.Amount}' --output table
```

Everything below the top ten is noise until the top is understood.

## Step 4 — Drill into usage type

Service totals hide the driver. This is the step that turns a number into a
finding:

```bash
aws ce get-cost-and-usage \
  --time-period Start=<start>,End=<end> --granularity MONTHLY --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["<service>"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --query 'ResultsByTime[0].Groups[].{Usage:Keys[0],Cost:Metrics.UnblendedCost.Amount}' --output table
```

For logs, the ingestion-versus-storage split is the important one — and
storage is usually a rounding error against ingestion.

## Step 5 — Attribute to an environment

```bash
aws ce get-cost-and-usage \
  --time-period Start=<start>,End=<end> --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=TAG,Key=Environment \
  --query 'ResultsByTime[0].Groups[].{Env:Keys[0],Cost:Metrics.UnblendedCost.Amount}' --output table
```

Untagged spend is common — report it as its own line rather than
distributing it by guess.

## Report

```
Account:   <id>   Period: <month>   Metric: UnblendedCost (pre-tax)
Total:     <amount>
Top services:
  1. <service>  <amount>   driver: <usage type>
By env:    <env> <amount> | untagged <amount>
Addressable: <amount>  (ranked recommendations in cost-report.md)
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Optimising before measuring | Breakdown first |
| Stopping at service level | Drill to usage type |
| Recommending retention cuts for log spend | Ingestion dwarfs storage |
| Mixing pre- and post-tax figures | State the metric every time |
| Distributing untagged spend by guess | Its own line |
| Exploring interactively | Each call is billed; plan the set |
