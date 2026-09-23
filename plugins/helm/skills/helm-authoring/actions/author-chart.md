# Action — Author Chart

Add or change a chart value, template, or dependency.

## Step 1 — Does this belong in the chart

| The value is… | Owner |
|---------------|-------|
| Static — probes, ports, env, replicas, resources, image tag | **this chart** |
| Computed — secret references, identity bindings, generated hostnames | the infrastructure layer; hand back |

Getting this wrong means the value never appears. Classify first.

## Step 2 — Reuse the chart's vocabulary

```bash
grep -rn "<related-key>" charts/<app>/values*.yaml
```

A second name for an existing concept is worse than a slightly awkward
existing name.

## Step 3 — Surface the key, then set it

Add it to `values.yaml` with a default **and** set the environment override:

```yaml
# values.yaml — the contract
resources:
  limits:
    memory: 512Mi

# values-staging.yaml — override only
resources:
  limits:
    memory: 1Gi
```

A key that exists only in an environment file is invisible to the next
reader.

## Step 4 — Library chart, if the chart delegates

If the library does not render the key at all, adding it is three steps: add
the template and default in the library, bump the dependency version in the
consumer, then surface the key. Skipping the version bump means the consumer
still resolves the old library.

## Step 5 — Render, do not reason

```bash
helm lint charts/<app>
helm template <app> charts/<app> -f charts/<app>/values.yaml -f charts/<app>/values-<env>.yaml
```

Render for **every** environment file, not just the one you changed — a
shared default can break another environment.

Confirm the rendered field is what you intended. `null` in particular often
does not override a default; `""` does.

## Step 6 — Versions

Bump `appVersion` if the deployed application version changed; bump the chart
`version` per the repo's convention.

## Report

```
Chart:     charts/<app>
Change:    <key> — <from> → <to>   (values.yaml + values-<env>.yaml)
Library:   <changed? version bumped?>
Rendered:  <the relevant rendered lines>
Envs:      rendered clean for <list>
Deploy:    a sync is required for this to take effect
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Setting a computed value in the chart | It belongs in the infrastructure layer |
| Adding a key only to an environment file | Surface it in `values.yaml` too |
| Duplicating a whole block into an environment file | Overrides only |
| `null` as a placeholder | Merge helpers skip nil; `""` overrides |
| Changing the library without bumping the dependency | The consumer resolves the old version |
| Rendering only the environment you touched | Render all of them |
| Concluding output from reading a template | Render it |
