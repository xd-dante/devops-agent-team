# Action — Inspect Rollout

A deployment is not progressing, or a new version never became live.

## Step 1 — Conditions, not just the ready count

```bash
kubectl rollout status deploy/<name> -n <ns> --timeout=10s
kubectl describe deploy <name> -n <ns> | sed -n '/Conditions:/,/Events:/p'
kubectl get rs -n <ns> -o custom-columns=NAME:.metadata.name,DESIRED:.spec.replicas,READY:.status.readyReplicas,IMAGE:.spec.template.spec.containers[0].image
```

| Condition | Reading |
|-----------|---------|
| `ProgressDeadlineExceeded` | New pods never went ready — triage the **new** ReplicaSet |
| `Available: False` | Not enough ready replicas for the strategy |
| `ReplicaFailure` | Pod creation is being rejected — quota, policy, or an admission webhook |

Old ReplicaSet still serving with the new one at zero ready means the new
version is broken and the old one is protecting you. Triage the new one.

## Step 2 — Is desired state even what you think

```bash
kubectl get deploy <name> -n <ns> -o jsonpath='{.spec.template.spec.containers[*].image}{"\n"}'
```

- Image is the old tag → desired state was never updated. The owner is the
  promotion agent or the GitOps agent, not this one.
- The deployment tool reports synced but the image is old → usually a pinned
  revision. `HANDOFF → argocd-agent`.

A rollout that never started is usually not a cluster problem.

## Step 3 — Admission and policy rejections

```bash
kubectl get events -n <ns> --sort-by=.lastTimestamp | grep -iE 'denied|forbidden|policy|webhook|quota' || true
```

Policy rules frequently live in a different repo than people assume — find
where before routing the fix.

## Report

```
Cluster:    <cluster>
Workload:   <ns>/deploy/<name>
Rollout:    <n>/<n> ready — condition: <condition>
Old RS:     <name> <ready> <image>
New RS:     <name> <ready> <image>
Blocked by: <new pods failing | desired state never changed | policy rejection>
Owner:      <agent> → <repo/file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `rollout restart` to kick it | Forbidden — find why it is stuck |
| Triaging the old ReplicaSet's healthy pods | Triage the new one |
| Assuming a stuck rollout is a pod problem | Check whether desired state ever changed |
| Guessing where policy rules live | Find the owning repo before routing |
