---
name: helm-authoring
description: 'Author, debug and review Helm charts — add or change values and templates, work with library-chart dependencies, find why a render does not produce what was expected, and review a chart change before it ships. Use when asked to change a chart value, add a template, debug a rendered manifest, or review chart changes.'
allowed-tools: Bash
---

# Helm Charts

Chart authoring and debugging. The chart is where **static** values live —
probes, ports, env vars, replicas, resources, image tags — and they reach the
cluster directly through the deployment tool's value-file reference.

**Rendering is the only proof.** Reading a template and concluding what it
produces is guesswork.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Author Chart | `actions/author-chart.md` | Add or change a value, template, or dependency |
| Debug Render | `actions/debug-render.md` | "It isn't producing what I expect" |
| Review Chart | `actions/review-chart.md` | Lint, render every environment, check the contract and runtime shape |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Chart Conventions | `standards/chart-conventions.md` | Structure, values contract, library charts, `null` vs `""`, security context |
| Checklist | `standards/checklist.md` | Pre-commit checks |

## Principles

1. **`values.yaml` is the contract** — every supported key appears there with
   a default; environment files carry overrides only.
2. **Render, do not reason** — and render for every environment file, not
   just the one you changed.
3. **`null` is not `""`** — merge helpers skip nil, so `null` leaves a
   default in place.
4. **A library chart that never reads a key renders nothing** — silently.
5. **Diff renders semantically** — key by `(kind, name, namespace)`; raw line
   diffs report reordering as change.
6. **`runAsNonRoot` needs a numeric uid** — a named `USER` cannot be verified
   by the kubelet.
7. **Static belongs here; computed does not** — classify before writing.

## Usage

1. Load this manifest and `standards/chart-conventions.md`.
2. Classify the value as static or computed.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md`.
