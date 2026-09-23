---
name: kargo-promote
description: 'Operate and debug container-image promotion pipelines — Freight and Warehouse state, Stage promotions, failed or silently no-op promotions, tag filters, revision pinning, and pipeline config changes. Use when asked what version is in which environment, why a promotion failed or changed nothing, why a new tag never became Freight, or for a Stage to be promoted. Read-only apart from the gated promotion action.'
allowed-tools: Bash
---

# Promotion Pipelines

The tool watches registries (Warehouses), turns new tags into Freight, and
promotes Freight through Stages by **committing to the chart repo** and then
forcing a sync.

**It does not deploy.** It edits git and asks the deployment tool to sync.
Every diagnosis starts there.

**Read-only by default.** One action mutates, and in later environments a
promotion is a real deploy.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Freight Status | `actions/freight-status.md` | What version is where; why a tag never became Freight |
| Troubleshoot Promotion | `actions/troubleshoot-promotion.md` | Failures, and "succeeded" promotions that changed nothing |
| Promote Stage | `actions/promote-stage.md` | **Gated, mutating.** One Freight, one Stage, whole chain verified |
| Pipeline Config | `actions/pipeline-config.md` | Warehouses, Stages, tasks, policy, tag filters |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Promotion Model | `standards/promotion-model.md` | Stage flow, policy, steps, tag keys, filters, pinning |
| Expression Rules | `standards/expression-rules.md` | Task-scoped outputs, no format function, where quoting belongs |
| Checklist | `standards/checklist.md` | Pre-promotion and pre-merge checks |

## Principles

1. **The tool commits; the deployment tool deploys** — if the commit did not
   land, nothing deployed, and the reason is in the steps.
2. **Read every step, never just the phase** — a succeeded promotion can have
   its commit and sync steps skipped. The most misleading signal here.
3. **No diff is not a fault** — say so before promoting, not after.
4. **Expression scope fails silently** — inside a task, bare `outputs` is
   nil, so the step skips forever.
5. **Auto-promotion is label-driven** — set the flag in values; the policy
   usually already exists.
6. **One pipelines chart** — a duplicate copy drifts silently.
7. **Merging does not deploy the pipeline** — the owning Application must be
   synced.

## Usage

1. Load this manifest and `standards/promotion-model.md`.
2. Resolve the cluster and the project namespace.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md` before promoting or merging.
