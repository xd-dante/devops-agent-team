# Action — Cross-Repo Change

A change that crosses a dependency chain — typically
infrastructure-as-code → GitOps definition → chart → library chart. Wrong
order here produces a merged PR that deploys nothing.

## Step 1 — Establish the chain

From `.devops-agents.yml` `repos` if present, otherwise infer: `*.tf` →
Terraform, `Chart.yaml` → Helm, Application/Stage manifests → GitOps or
promotion. Read `.gitmodules` for submodule edges.

## Step 2 — Classify the value

The single question that decides which repos are involved:

| Kind | Examples | Path |
|------|----------|------|
| **Static** | probes, ports, env vars, replicas, resources, image tag | Chart values files, read directly by the GitOps source. **Bypasses the infrastructure layer.** |
| **Computed** | secret references, identity role bindings, security groups, generated hostnames | Set in the infrastructure module, shaped into the Application's inline values |

Classify before dispatching. Half of "the value isn't taking effect" is a
value set on the wrong path.

## Step 3 — Read base-branch truth, never a worktree

```bash
git -C <repo> fetch
git -C <repo> show origin/<base>:<path>
```

Worktrees may be stale or dirty. Use them to apply changes, never to validate
what upstream currently says.

## Step 4 — Propagate

**Static — validate bottom-up, fix at the lowest owning layer:**

1. Does the chart surface the key, **and** does the library chart render it?
   - both yes → set it in the chart's values. Done.
   - library renders it, chart does not surface it → add the key, then set it.
   - library does not render it → add the template and default in the library
     chart, bump the dependency version, surface the key, then set it.
2. The infrastructure layer usually needs **no change** — its value-files
   reference already pulls the chart values.

**Computed:**

1. Wire the value in the infrastructure module call.
2. Make the GitOps module shape it into the Application's values. Keep any
   parallel resource variants in sync — they drift silently.
3. Make the chart and library chart consume the rendered value.

## Step 5 — State the order explicitly

Dependencies merge first, consumers second. Name the order in the report;
never leave the user to infer it.

If the Application pins its target revision to a commit or tag, merging the
chart PR alone deploys nothing — the pin must move too. Route that to
`argocd-analyst`.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Setting a static value in the infrastructure layer | It is bypassed; set it in the chart |
| Reading a worktree as validation source | `git show origin/<base>:<path>` |
| Editing one of two parallel resource variants | Both, always |
| Merging a chart PR against a pinned revision | Move the pin, or nothing deploys |
| Assuming `null` and `""` are the same placeholder | Merge helpers often skip nil; `""` overwrites, `null` may not |
| Committing a submodule pointer with the parent | Separate branch and PR; the pin stays on base |
