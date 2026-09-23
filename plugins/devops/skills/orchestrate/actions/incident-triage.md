# Action — Incident Triage

"X is broken in \<env\>." Parallel read-only fan-out, one root cause, a
routed recommendation. **Nothing is mutated by this action.**

## Step 1 — Pin the target

Establish and echo back before dispatching anything:

```
Service:     <app>
Environment: <env>
Cluster:     <resolved cluster name>
Profile:     <cloud profile for that environment>
Symptom:     <what the user actually observes>
```

**🛑 STOP** if the environment is unstated. Never assume. For a protected
environment, echo the target back and get confirmation before any command
runs.

## Step 2 — Fan out (parallel, read-only)

| Agent | Question it answers |
|-------|--------------------|
| `kubernetes-investigator` | What does the workload say — restarts, probes, OOM, scheduling, events? |
| `argocd-analyst` | Is desired state what we think — synced, drifted, pinned revision, last sync result? |
| `aws-investigator` | Is a dependency below the cluster failing — database, secrets, IAM, quotas? |
| `kargo-promoter` | Only if the symptom is version-shaped ("wrong version", "deploy never arrived") |

Each brief carries the pinned block from step 1 verbatim and asks for
evidence-backed findings only.

## Step 3 — Consolidate

Build one timeline: what changed, when, what broke after it. Then:

- Reconcile. Pod-level evidence usually explains a GitOps status; the reverse
  rarely holds.
- Conflict on a fact that changes the fix → name it and the single cheapest
  settling check.
- Nothing proven → rank hypotheses and label them as hypotheses.

## Step 4 — Recommend, do not apply

```
Recommended fix (not applied):
  - <change>  → route: terraform-engineer (<repo>, targeted plan)
  - <change>  → route: helm-engineer (<chart>/values-<env>.yaml)
```

Live cluster mutation is out of bounds here — the cluster agent is read-only
and GitOps owns desired state. If the user then wants the fix, re-enter
through `actions/route-task.md` with the mutation acknowledged and the
environment confirmed.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Investigating before the environment is pinned | Step 1, every time |
| Serial fan-out | These are disjoint reads — parallel |
| Patching because the fix is obvious | Recommend; GitOps or a targeted apply owns it |
| Averaging conflicting reports | Name the conflict and the settling check |
| Reporting a symptom as a root cause | "OOMKilled" is the symptom; the limit is the cause |
