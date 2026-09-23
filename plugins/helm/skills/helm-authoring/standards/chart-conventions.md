# Chart Conventions

## Structure

```
charts/<app>/
  Chart.yaml            name, version, appVersion, dependencies
  values.yaml           defaults — every key the chart supports, documented
  values-<env>.yaml     per-environment overrides only
  templates/
  templates/tests/
```

`version` is the chart's own version; `appVersion` is the application's.
Bumping the app's image without bumping `appVersion` leaves the chart lying
about what it deploys.

## Values

- **`values.yaml` is the contract.** Every supported key appears there with a
  sane default, even when the default is empty. A key only set in an
  environment file is invisible to anyone reading the chart.
- **Environment files carry overrides only** — not a full copy. A duplicated
  block drifts.
- Group by concern (`image`, `resources`, `probes`, `ingress`), not
  alphabetically.
- Never commit a real secret. Reference a secret store; leave a placeholder.

## `null` is not an empty string

Merge helpers commonly **skip nil values**, so `key: null` does not override
a default — it leaves it in place. `key: ""` is a real value and does
override.

This matters when seeding a placeholder that automation will later overwrite:
`null` renders the library's own default forever, which is rarely what was
intended. Verify with a render, not by reasoning.

## Library charts

When a chart delegates rendering to a shared library:

- a key the chart surfaces but the library never reads renders as **nothing**
  — silently
- adding a capability means: template and default in the library, version
  bump in the consumer's dependency, then surface the key in the consumer's
  `values.yaml`
- keep the library's own defaults and the consumer's surfaced keys in step;
  they drift in opposite directions otherwise

## Rendering is the only proof

```bash
helm template <release> <chart> -f values.yaml -f values-<env>.yaml
```

Reading a template and concluding what it produces is guesswork. Render it.

For a multi-document render, diff **semantically** — parse and key by
`(kind, metadata.name, metadata.namespace)`. Adding one document shifts every
later document's position, so a raw line diff reports unrelated content as
changed.

## Security context

`runAsNonRoot: true` **alone** fails when the image's `USER` is a name rather
than a numeric uid — the kubelet cannot verify it. Pair it with an explicit
numeric `runAsUser` (and `runAsGroup`) matching the image's built-in user.
Get the value from the image; do not guess it.

A chart's security context can also override an image that is already
correctly non-root, so check the **rendered** spec rather than the Dockerfile.

## Commits in chart repos

Where a repo's hooks regenerate documentation, bump versions, or update
lockfiles, those generated files pollute the diff. Committing with
`--no-verify` is legitimate there — say so, and keep generated files out of
the commit.
