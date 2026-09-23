# Action — App Health Triage

An Application is degraded, progressing, out of sync, missing, or unknown.
Establish what the status actually means.

## Step 1 — Read all of it, not the first field

```bash
kubectl get application -n <ns> <app> -o jsonpath='{.status.sync.status} {.status.health.status} {.status.sync.revision} {.spec.source.targetRevision}{"\n"}'
kubectl get application -n <ns> <app> -o jsonpath='{.status.operationState.phase}: {.status.operationState.message}{"\n"}'
argocd app get <app>
```

## Step 2 — Interpret the combination

| Sync | Health | Reading |
|------|--------|---------|
| Synced | Healthy | The tool is satisfied. If the app still misbehaves, desired state itself is wrong — a chart or infrastructure problem |
| Synced | Degraded | Manifests applied, workload failing. `HANDOFF → kubernetes-investigator` for the pod-level cause |
| Synced | Progressing | A rollout is in flight or stuck. `HANDOFF → kubernetes-investigator` |
| OutOfSync | Healthy | Merged changes not yet deployed. **Expected** where automated sync is off |
| OutOfSync | Degraded | Two problems. Fix the broken workload before syncing new changes on top |
| Unknown | Unknown | Repo unreachable, invalid manifests, or a missing revision — read `operationState.message` |
| Missing | — | Resources absent; often a namespace or a failed first sync |

## Step 3 — The last operation carries the real error

`operationState.message` names admission rejections, immutable-field
conflicts, missing CRDs, and render failures. **Quote it verbatim.**

An immutable-field error (a selector, a cluster IP, volume templates) means
the change cannot be applied in place at all — a chart finding needing a
planned replacement, not a retry.

## Step 4 — Find the unhealthy resource

```bash
kubectl get application -n <ns> <app> -o jsonpath='{range .status.resources[*]}{.kind}/{.name} {.health.status}{"\n"}{end}'
```

One unhealthy resource degrades the whole Application. Find it before
diagnosing the app as a whole.

## Report

```
Cluster:    <cluster>
App:        <app>   (owned by: <repo>)
Sync:       <status> @ <revision>   targetRevision: <value>
Health:     <status>
Last op:    <phase> — <message verbatim>
Unhealthy:  <kind/name> — <reason>
Root cause: <explanation or ranked hypotheses>
Owner:      <agent> → <repo/file>
Nothing was synced or mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading health alone | Read sync, health, revision and operationState together |
| Treating out-of-sync as a fault | Where automated sync is off, it is normal after a merge |
| Syncing to "clear" a degraded app | A broken workload stays broken |
| Paraphrasing `operationState.message` | Quote it; it names the real error |
| Diagnosing the app when one resource is unhealthy | Find the resource first |
| Calling an app unmanaged | Check every infrastructure repo |
