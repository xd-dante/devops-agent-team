# Action — Promote Stage

**Mutating.** A promotion commits to the chart repo and forces a sync. In
later environments that is a real deploy.

## Gate — all required

- [ ] User approved **this app**, **this Stage**, and **this run**
- [ ] The Freight is identified explicitly, with its tag
- [ ] Whether this is a real version change or a same-version no-op is stated
      **before** promoting
- [ ] The downstream effect is stated: which environment actually redeploys
- [ ] Protected environments confirmed separately

Any box unticked → **🛑 STOP**.

## Step 1 — Identify the delta

```bash
kubectl get freight -n <project-ns> --sort-by=.metadata.creationTimestamp | tail -5
kubectl get stage <app>-<env> -n <project-ns> -o jsonpath='{.status.freightHistory[0]}{"\n"}'
git -C <chart-repo> show origin/<base>:charts/<app>/values-<env>.yaml | grep -iE 'tag:' || true
```

Three things get compared: the Freight's tag, what the Stage runs, and what
the values file says.

If the values file already carries the promoted tag, the promotion is a
**no-op**: the update step succeeds, commit and sync skip, no health check is
registered. Say this **before** promoting, not after.

## Step 2 — Check the gate and the key

```bash
kubectl get stage <app>-<env> -n <project-ns> -o jsonpath='{.spec.requestedFreight}{"\n"}'
git -C <chart-repo> show origin/<base>:charts/<app>/values-<env>.yaml | grep -nE 'image:|tag:' || true
```

A Stage requesting Freight from an upstream Stage can only take what passed
it. A missing tag key fails the promotion — the update step cannot create
one.

## Step 3 — Promote

One Stage, one Freight, per approval. Never a set. The tool's UI is usually
the better path for an interactive promotion.

## Step 4 — Verify the whole chain

A promotion is done only when four links hold:

```bash
# 1. steps
kubectl get promotion <name> -n <project-ns> -o jsonpath='{range .status.steps[*]}{.alias}: {.status}{"\n"}{end}'
# 2. the commit landed
git -C <chart-repo> fetch && git -C <chart-repo> log --oneline -3 -- charts/<app>/values-<env>.yaml
# 3. the deployment moved
kubectl get application -n <argo-ns> <app>-<env> -o jsonpath='{.status.sync.revision} {.status.health.status}{"\n"}'
# 4. the workload is healthy — HANDOFF → kubernetes-investigator
```

## Report

```
Promoted:   <app>-<env>   Freight <id> (tag <tag>)
Delta:      <old> → <new>   (real change | same-version no-op)
Steps:      <alias>: <status> for each
Commit:     <sha>
Deployment: <revision before> → <after>   sync <status>  health <status>
Workload:   <verified by kubernetes-investigator | not verified>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Promoting without checking for a diff | A no-op registers nothing; say so upfront |
| Treating "promotion succeeded" as done | Verify commit, revision, and pods |
| Promoting a set of stages on one approval | One Stage, one Freight, one approval |
| Not saying a later environment redeploys | These are real deploys |
| Forgetting the tag key must pre-exist | Check the values file first |
