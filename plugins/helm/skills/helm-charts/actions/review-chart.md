# Action — Review Chart

Review a chart or a chart change before it ships.

## Step 1 — Lint and render everything

```bash
helm lint charts/<app>
for f in charts/<app>/values-*.yaml; do
  echo "== $f"
  helm template <app> charts/<app> -f charts/<app>/values.yaml -f "$f" > /dev/null || echo FAILED
done
```

A change that renders in one environment and breaks another is the most
common chart regression.

## Step 2 — Check the contract

- Is every new key in `values.yaml` with a default?
- Do environment files carry **only** overrides?
- Does `appVersion` match what is actually deployed?
- Is the library dependency version bumped if the library changed?

## Step 3 — Check the runtime shape

| Area | What to look for |
|------|------------------|
| Resources | Requests set (they drive scheduling), limits sane relative to observed usage |
| Probes | Readiness path and port match what the app serves; initial delay covers real startup |
| Security context | `runAsNonRoot` paired with a **numeric** uid; no unnecessary root |
| Service | Port chain lines up: service port → target port → container port |
| Labels | Selectors actually match the pod labels |
| Secrets | Referenced, never inlined |

## Step 4 — Read the deletions

```bash
git diff origin/<base>...HEAD -- charts/<app>
```

Three dots, against the merge base. Read every removed line: a
wholesale-rewritten values file silently drops keys, and a two-dot diff mixes
in the base's newer commits so real losses hide among noise.

## Step 5 — Report findings, most severe first

```
Chart:     charts/<app>
Lint:      clean | <findings>
Renders:   <n>/<n> environment files render
Contract:  <keys missing from values.yaml, duplicated blocks>
Runtime:   <resources, probes, security context, port chain findings>
Deletions: <anything removed that looks unintended>
Verdict:   <ship | changes needed>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Rendering one environment only | Render all of them |
| Reviewing the diff without rendering | Render is the only proof |
| Two-dot diff | Three dots, against the merge base |
| Skipping removed lines | A rewritten values file drops keys silently |
| Approving `runAsNonRoot` without a numeric uid | It fails at container start |
