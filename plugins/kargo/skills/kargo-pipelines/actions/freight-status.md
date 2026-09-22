# Action — Freight Status

"What version is where", "is there new Freight", "why hasn't dev picked up
the new tag".

## Step 1 — Warehouses and Stages

```bash
kubectl get warehouse,stage,freight -n <project-ns>
kubectl get freight -n <project-ns> --sort-by=.metadata.creationTimestamp | tail -20
kubectl get stage <app>-<env> -n <project-ns> -o jsonpath='{.status.freightHistory[0]}{"\n"}'
```

Read `status.freightHistory[0]` for what is **live**; `spec.requestedFreight`
for what the Stage is allowed to take.

## Step 2 — No new Freight? Check the tag filter first

```bash
kubectl get warehouse <app> -n <project-ns> -o jsonpath='{.spec.subscriptions[*]}{"\n"}'
```

An allow-list pattern excludes anything not matching — pre-release tags are
the usual casualty. This is deliberate, pipeline-wide, and applies to
**future** tags only, so Freight created before the filter still exists.

Tag matches and still nothing appeared → read the Warehouse status and the
controller logs rather than guessing:

```bash
kubectl describe warehouse <app> -n <project-ns> | sed -n '/Status:/,$p'
kubectl logs -n <controller-ns> -l <controller-selector> --tail=100 | grep -i <app> || true
```

## Step 3 — Stage not taking available Freight

| Cause | Signal |
|-------|--------|
| Upstream gate not satisfied | `sources.stages` names an upstream Stage the Freight has not passed |
| Auto-promote not enabled | The Stage lacks the auto-promote label — later environments are manual by design |
| Shard mismatch | The Stage's shard has no running controller |

## Report

```
App:        <app>
Warehouse:  <name> — latest Freight <id> (tag <tag>, created <ts>)
Tag filter: <pattern> — does the expected tag match?
Stages:     dev <tag> | test <tag> | staging <tag> | production <tag>
Blocked:    <which stage, and why — gate | manual by design | no Freight>
Nothing was promoted.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Assuming a pushed tag becomes Freight | Check the allow-list pattern first |
| Expecting a new filter to remove old Freight | It applies to future tags only |
| Calling a manual Stage "stuck" | Later environments are manual by design |
| Reading `spec` for what is live | `status.freightHistory[0]` is what runs |
