# Action — Pipeline Config

Changing the pipelines chart: Warehouses, Stages, promotion tasks, policy,
tag filters.

## Step 1 — One chart only

Pipelines live in one chart. Where a duplicate copy exists with no dependency
link between them, every fix has to be applied twice and they drift silently
— consolidate rather than maintaining both, and never introduce a second
copy.

## Step 2 — Prefer values over templates

| Ask | Change |
|-----|--------|
| Auto-promote an environment | Set the auto-promote flag for that environment — the label-selector policy usually already exists, so **no policy change is needed** |
| Restrict which tags become Freight | The Warehouse subscription's allow-list — pipeline-wide, no per-Stage equivalent |
| Fix the image tag key for an app | That app's tag-key setting |
| Pin the deployment revision for a Stage | That Stage's pin flag |

Reach for the template only when the values key does not exist yet.

## Step 3 — Diff renders semantically

A raw line diff of a multi-document YAML render is misleading: adding one
document shifts every later document's position, so unrelated content appears
to change.

Parse both renders and diff by `(kind, metadata.name, metadata.namespace)`.
Raw diffs routinely produce dozens of false "differences" that are pure
reordering.

## Step 4 — Check secret templates against live state

If the chart renders a credentials secret and the live secret already carries
real values from another mechanism, a template with blank placeholders will
**overwrite them and break git auth for every promotion**.

Verify live before merging. This is a merge blocker, not a post-merge check.

## Step 5 — Expressions

Any change touching the promotion task must satisfy
`standards/expression-rules.md`. A wrong scope reference does not error — it
evaluates to nil and silently skips the step.

## Step 6 — After merge, a sync is required

The pipelines chart is deployed by an Application that may have automated
sync off. **Merging alone does not land a new promotion task** — the owning
Application must be synced. Say so explicitly; a promotion run before that
sync fails with the old task.

## Report

```
Chart:       <pipelines chart path>
Change:      <values | template> — <what>
Render diff: <semantic summary, by (kind,name,namespace)>
Secrets:     <live state checked? safe to adopt?>
Expressions: <verified | n/a>
Post-merge:  sync the owning Application — <app name>
Owner:       helm-agent for chart mechanics; kargo-agent for pipeline semantics
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Editing a second copy of the chart | One chart; consolidate duplicates |
| Changing the policy to add auto-promotion | The label selector usually already covers it |
| Raw line-diffing the render | Diff by `(kind, name, namespace)` |
| Merging a secret template unchecked | Verify the live secret first |
| Expecting a merge to deploy the new task | The Application must be synced |
| Bare `outputs` inside a task | `task.outputs[...]` |
