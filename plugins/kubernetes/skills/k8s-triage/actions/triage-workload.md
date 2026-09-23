# Action — Triage Workload

A pod or deployment is unhealthy. Find out why, read-only.

## Step 1 — Context, echoed

Resolve and switch per `standards/cluster-discovery.md`, then echo:
`Investigating on: <cluster> (context: <name>)`

## Step 2 — Scope and evidence

```bash
kubectl get pods -A -o wide | grep -iE 'crash|error|pending|0/|imagepull|evict' || true
kubectl get deploy,sts,ds,rs,pods -n <ns> -o wide
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> [-c <container>]
kubectl logs <pod> -n <ns> [-c <container>] --previous     # the crash before this one
kubectl get events -n <ns> --sort-by=.lastTimestamp | tail -30
```

`--previous` is where the actual failure usually is. Current logs often show
a healthy start followed by nothing.

## Step 3 — Classify

| Signal | Reading |
|--------|---------|
| `terminated.reason: OOMKilled` | Limit too low, or a leak. Compare `top pod` against the limit |
| `CrashLoopBackOff` + immediate exit | Startup failure — config, missing secret or env, failed migration. Read `--previous` |
| `Readiness probe failed` | Up but not serving on the probe path or port |
| `Liveness probe failed` + periodic restarts | Probe too aggressive, or a genuine hang. Compare `initialDelaySeconds` with real startup time |
| `ImagePullBackOff` | Tag missing, or registry auth. **Verify the tag exists** before blaming auth |
| `Pending` + `FailedScheduling` | Nothing fits — see `actions/node-capacity.md` |
| `CreateContainerConfigError` | A referenced secret or config key is missing |
| `non-numeric user` error | The image's `USER` is a name; a numeric `runAsUser` is required |
| `Init:*` stuck | An init container is failing — log it with `-c` |

## Step 4 — What changed

```bash
kubectl rollout history deploy/<name> -n <ns>
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].image}{"\n"}'
```

A failure that began at a deploy is a different investigation from one that
began on its own. If the image moved, the version question is
`kargo-promoter`'s.

## Report

```
Cluster:    <cluster>  (context: <name>)
Workload:   <ns>/<kind>/<name>       Image: <image:tag>
Symptom:    <observed>
Evidence:   <events, terminated reason, key log lines>
Root cause: <best-supported explanation, or ranked hypotheses>
Owner:      <agent> → <repo/file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading only current logs | `--previous` on anything that restarted |
| Calling OOMKilled the root cause | It is the symptom; the limit or leak is the cause |
| Blaming registry auth on an image pull failure | Verify the tag exists first |
| Patching resources to test a theory | Read-only; recommend the chart change |
| Skipping "what changed" | A deploy-triggered failure has a different owner |
