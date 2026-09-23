# Action — Desired vs Live

"The value I set is not taking effect."

## Step 1 — Classify the value path first

This decides which repo you are even looking in:

| Kind | Lives in | Reaches the app via |
|------|----------|---------------------|
| **Static** — probes, ports, env, replicas, resources, image tag | chart values files | `source.helm.valueFiles` — **bypasses module value shaping entirely** |
| **Computed** — secret references, identity bindings, generated hostnames | infrastructure module call | shaped into `valuesObject` / `parameters` |

A static value set in infrastructure code never appears. A computed value
written into a chart's values is ignored or overwritten. Getting this wrong
is the most common cause of the symptom.

## Step 2 — What does the Application actually request

```bash
kubectl get application -n <ns> <app> -o jsonpath='{.spec.source.repoURL}{"\n"}{.spec.source.path}{"\n"}{.spec.source.targetRevision}{"\n"}'
kubectl get application -n <ns> <app> -o jsonpath='{.spec.source.helm.valueFiles}{"\n"}'
```

Check the environment-specific values file is actually **listed**. An app
missing it silently ignores everything in that file.

## Step 3 — Is the requested revision the one you changed

A pinned target revision means your merged commit is not being tracked at
all → `actions/revision-pin.md`.

## Step 4 — Diff

```bash
argocd app diff <app>
argocd app manifests <app> > /tmp/desired.yaml
```

Compare against what git renders, from **base-branch truth** rather than a
worktree:

```bash
git -C <chart-repo> fetch
git -C <chart-repo> show origin/<base>:charts/<app>/values-<env>.yaml
helm template <app> <chart-repo>/charts/<app> -f <values> -f <values-env>
```

- git renders it, live does not → the gap is in the Application spec (wrong
  value files, wrong path, pinned revision) — an infrastructure finding
- git does not render it either → the gap is in the chart or library chart —
  a `helm-engineer` finding

## Step 5 — Library-chart traps

- A key the chart surfaces but the library never reads renders as nothing.
- `null` and `""` are **not** equivalent. Merge helpers commonly skip nil
  values, so `key: null` never overwrites a library default while `key: ""`
  does.

## Report

```
App:         <app>   Cluster: <cluster>
Value:       <key>   Classified as: static | computed
Requested:   repo <url> path <path> rev <targetRevision>
valueFiles:  <list>   (environment file present? yes/no)
Git renders: yes | no      Live has it: yes | no
Gap:         <Application spec | chart | library chart>
Owner:       <terraform-engineer | helm-engineer>
Nothing was synced or mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Diffing before classifying the value path | Classify first; it decides the repo |
| Reading a worktree as git truth | `git show origin/<base>:<path>` |
| Missing that the environment values file is absent | Check the list explicitly |
| Treating `null` as an empty-string placeholder | Merge helpers skip nil; use `""` |
| Ignoring a pinned revision | Check it before anything else |
