# Action — Troubleshoot Promotion

A promotion failed, or "succeeded" without changing anything.

## Step 1 — Read the per-step phases

This is the whole action in one step. A promotion can report **succeeded**
with its most important steps **skipped**.

```bash
kubectl get promotion -n <project-ns> --sort-by=.metadata.creationTimestamp | tail -10
kubectl get promotion <name> -n <project-ns> -o jsonpath='{range .status.steps[*]}{.alias}: {.status}{"\n"}{end}'
```

## Step 2 — Match the symptom

| Steps | Reading |
|-------|---------|
| Values update fails, key-path error | The image tag key does not exist in the environment's values file. The step **cannot create** it — it must be seeded with a real value. Also check the key shape for that chart |
| Commit and sync steps both skipped, everything else succeeded | **No diff** — the seeded tag already equals the promoted tag. Expected. No commit means no sync and no health check |
| The sync step skipped while commit succeeded | An expression scope bug — inside a task the reference must be `task.outputs['...']`. See `standards/expression-rules.md` |
| Push fails on auth | The chart-repo credentials secret. Check it exists and is **populated** before assuming the template is wrong |
| Sync step fails | The Application may lack the integration annotation, or the Stage name may not match the Application name |
| No promotion created at all | Not a promotion problem — see `actions/freight-status.md` |

## Step 3 — The integration annotation

```bash
kubectl get application -n <argo-ns> <app>-<env> -o jsonpath='{.metadata.annotations}{"\n"}' | tr ',' '\n' | grep -i <tool> || true
```

It is set by whatever generates the Application. Beware name mismatches — an
Application and its Stage can be named differently, which needs an explicit
override. **Never hand-patch it**: the next apply removes it silently.

## Step 4 — Was the effect real

```bash
git -C <chart-repo> log --oneline -5 -- charts/<app>/values-<env>.yaml
kubectl get application -n <argo-ns> <app>-<env> -o jsonpath='{.status.sync.revision} {.status.sync.status}{"\n"}'
```

The sync step forces a sync by mutating the Application's operation directly,
so it works even where automated sync is off. Commit landed but the
deployment did not move → that is a GitOps finding.

## Report

```
Promotion:  <name>   Stage: <app>-<env>   Freight: <id> (tag <tag>)
Steps:      <alias>: <status> for each
Diagnosis:  <no diff | missing key | expression scope | auth | annotation>
Commit:     <sha or none>   Deployment revision: <before> → <after>
Owner:      <kargo-promoter (chart) | terraform-engineer (annotation) | argocd-analyst>
Nothing was promoted.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading only the overall phase | Read every step's status |
| Treating a skipped step as harmless | A skipped sync means no deployment and no health check |
| Blaming a no-op promotion on configuration | Confirm whether there was a diff at all |
| Assuming `outputs.x` works inside a task | `task.outputs['x']`; bare is nil |
| Hand-patching the integration annotation | The owning code reverts it |
| Assuming the git push means it deployed | Check the deployment's revision moved |
