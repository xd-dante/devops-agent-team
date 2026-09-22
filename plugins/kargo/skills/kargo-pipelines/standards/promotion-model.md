# Promotion Model

## What the tool actually does

A promotion tool watches container registries (**Warehouses**), turns new tags
into **Freight**, and promotes Freight through **Stages** by
**committing to the chart repo** and then forcing the deployment tool to
sync.

**It does not deploy.** It edits git and asks the deployment tool to sync.
Every diagnosis starts there.

## Stage flow

```
Warehouse (registry subscription)
   → Freight
   → dev Stage       (auto-promote)
   → test Stage      (auto-promote; requests Freight that passed dev)
   → staging Stage   (manual)
   → production      (manual)
```

`requestedFreight.sources.stages` is the gate: a downstream Stage requests
Freight that has already passed an upstream one. So auto-promoting a Stage
removes a manual click **without** bypassing the upstream gate.

## Auto-promotion is usually label-driven

A project-level config typically carries a promotion policy selecting Stages
by label:

```yaml
promotionPolicies:
  - autoPromotionEnabled: true
    stageSelector:
      matchLabels:
        <tool>/auto-promote: "true"
```

Where that policy already exists, adding an environment to auto-promotion is
a **values change** that sets the label — not a policy change. Check before
editing the policy.

## Promotion steps

A shared promotion task typically runs:

1. `git-clone` — clone the chart repo
2. `update-values` — write the new tag into the environment's values file
3. `git-commit`
4. `git-push`
5. `argocd-update` (or equivalent) — force a sync, optionally pinning the
   deployment's target revision to the promoted commit

**Steps 3–5 are conditional.** No diff means no commit, which means no sync
step, which means no health check is registered. That is expected behaviour,
not a fault — and it is the single most misread signal in the system.

## The image tag key

The update step writes to a key path that depends on the chart's shape:

| Chart shape | Typical key |
|-------------|-------------|
| single service | `image.tag` |
| multi-service via a library chart | `<prefix>.image.tag` |

Configured per app. **The update step cannot create a missing key** — it must
already exist in the environment's values file, seeded with a real value. An
absent key fails the promotion with a key-path error.

## Tag filtering

A tag-pattern allow-list on the Warehouse's subscription restricts which tags
become Freight — for example, strict release tags only, excluding
pre-releases.

It applies **per Warehouse**, which means pipeline-wide: there is no
per-Stage tag-format gate. Filters affect **future** tags only; Freight
created before the filter existed is not removed retroactively.

## Revision pinning

Pinning the deployment's target revision to the exact promoted commit stops a
floating branch head racing ahead when another app promotes on the same
branch. Without it a Stage can show unhealthy while the deployment tool shows
synced. Usually set on the environments downstream of dev.
