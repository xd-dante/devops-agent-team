# Action — Debug Render

"The chart isn't producing what I expect."

## Step 1 — Render exactly what the deployment renders

```bash
helm template <release> charts/<app> \
  -f charts/<app>/values.yaml \
  -f charts/<app>/values-<env>.yaml > /tmp/rendered.yaml
```

Use the **same value files, in the same order**, as the deployment. Order
matters: later files win, and a missing file changes the result silently.

Check which files the deployment actually passes — an environment file absent
from that list is ignored entirely, which looks exactly like a broken
template.

## Step 2 — Find the field, do not skim

```bash
grep -n -A5 '<field>' /tmp/rendered.yaml
```

Absent from the render → the template never emitted it. Present but wrong →
a values problem. Those are different investigations.

## Step 3 — Classify why it is absent

| Cause | Check |
|-------|-------|
| The library chart never reads the key | Search the library's templates for it |
| The chart does not surface the key | It is missing from `values.yaml` |
| A nil placeholder | `null` does not override a default; `""` does |
| A guard excludes it | Find the `if` around the block |
| The value is computed elsewhere | It arrives from the infrastructure layer, not the chart |

## Step 4 — Compare against live

```bash
kubectl get <kind> <name> -n <ns> -o yaml
```

Render and live disagree → the deployment has not synced, or it is pinned to
an older revision. That is a GitOps finding, not a chart one:
`HANDOFF → argocd-agent`.

## Step 5 — Diffing two renders

Parse both and compare by `(kind, metadata.name, metadata.namespace)`. A raw
line diff of multi-document YAML reports pure reordering as change — adding
one document shifts every later one.

## Report

```
Chart:     charts/<app>     Values: <files, in order>
Expected:  <field> = <value>
Rendered:  <what actually appears, or absent>
Cause:     <library | chart | nil placeholder | guard | computed elsewhere>
Live:      <matches render? if not, sync or pin>
Owner:     <helm-agent | terraform-agent | argocd-agent>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Rendering with different value files than the deployment | Match the list and the order |
| Missing that an environment file is not in the deployment's list | Check it explicitly |
| Treating absent and wrong as the same problem | They have different causes |
| Assuming `null` behaves like `""` | Merge helpers skip nil |
| Blaming the chart when live differs from the render | Check sync state and the pin |
| Raw line-diffing a multi-document render | Diff by `(kind, name, namespace)` |
