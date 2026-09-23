# Action — Node Capacity

Pods are `Pending`, nodes look pressured, or autoscaling is not providing
capacity.

## Step 1 — Read the scheduling message literally

```bash
kubectl describe pod <pod> -n <ns> | sed -n '/Events:/,$p'
```

| Message | Reading |
|---------|---------|
| `Insufficient cpu` / `memory` | Requests exceed free allocatable. Fix requests (chart) or add capacity (infrastructure) |
| `had untolerated taint` | Missing a toleration for the pool it needs |
| `didn't match Pod's node affinity/selector` | Targets labels no node has |
| `unbound immediate PersistentVolumeClaims` | Storage or zone problem, **not** capacity |
| `too many pods` | Per-node pod or interface limit reached |
| `Insufficient <network-interface resource>` | Dedicated pod-interface slots exhausted on that instance type |

## Step 2 — Requests vs usage

```bash
kubectl describe node <node> | sed -n '/Allocated resources:/,/Events:/p'
kubectl top nodes
```

**Scheduling uses requests, not usage.** A node at 30% real usage can be
unschedulable because requests are booked.

## Step 3 — Autoscaler

```bash
kubectl get nodepool,nodeclass -o wide 2>/dev/null
kubectl logs -n <autoscaler-ns> -l app.kubernetes.io/name=<autoscaler> --tail=100 | grep -iE 'error|cannot|unable|no instance' || true
```

Not scaling up is usually: requirements no instance offering satisfies, a
pool limit already reached, a subnet or security-group selector matching
nothing, or a zone with no capacity for the requested type. **The logs say
which** — read them rather than inferring. Pool definitions are owned by the
infrastructure repo.

## Step 4 — Pressure

```bash
kubectl get events -A --sort-by=.lastTimestamp | grep -iE 'evict|pressure|OutOfmemory' || true
```

Disk pressure is frequently image-cache growth, not application data.

## Report

```
Cluster:    <cluster>
Pending:    <n> pods — reason: <verbatim scheduling message>
Nodes:      <n> ready; requests <x>% cpu, <y>% mem; usage <a>%/<b>%
Autoscaler: <provisioning? blocking reason from logs>
Pressure:   <conditions>
Owner:      <helm-engineer (requests/tolerations) | terraform-engineer (pools)>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `cordon` / `drain` / `taint` to rebalance | Forbidden — read-only |
| Reading `top` as scheduling capacity | Scheduling uses requests |
| Assuming the autoscaler is broken | Read its logs; the reason is stated |
| Treating an unbound claim as capacity | It is storage or zone |
| Editing a node pool in place | Owned by the infrastructure repo |
