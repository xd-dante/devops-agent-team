# Action — Sync Application

**Mutating.** A sync deploys whatever the source repo currently says.

## Gate — all required

- [ ] User approved **this app** and **this run** explicitly
- [ ] The diff was shown to the user first
- [ ] Other people's merged-but-unsynced changes in that diff were surfaced
- [ ] A protected environment, if targeted, was confirmed separately
- [ ] Prune off, or the exact resources to be deleted were shown

Any box unticked → **🛑 STOP**.

## Step 1 — Show the diff first

```bash
argocd app diff <app>
```

This is the point of the gate. An app that has been out of sync for a while
may carry several people's merged changes — syncing deploys all of them, not
just the one the user has in mind. **Name them.**

## Step 2 — Confirm what revision will deploy

```bash
kubectl get application -n <ns> <app> -o jsonpath='{.spec.source.targetRevision}{"\n"}'
```

Pinned → a sync will **not** pick up newer commits. Stop and route to
`actions/revision-pin.md` rather than syncing and reporting success.

## Step 3 — Sync

```bash
argocd app sync <app>
```

Deliberately not used:

| Flag | Why not |
|------|---------|
| `--prune` | Deletes live resources absent from git — needs its own approval with the list shown |
| `--force` / `--replace` | Delete and recreate resources; data-loss risk |
| `--async` | You must observe the result |
| label selectors / all apps | One app per approval |

## Step 4 — Watch the result

```bash
kubectl get application -n <ns> <app> -o jsonpath='{.status.operationState.phase}: {.status.operationState.message}{"\n"}'
```

A failed phase with an immutable-field error means the change cannot be
applied in place — a chart finding needing a planned replacement. **Do not
retry unchanged.**

## Step 5 — Verify the workload, not the sync

Sync success means manifests applied, not that the app works.
`HANDOFF → kubernetes-agent` (read-only) to confirm pods went ready, and say
in the report who verified it.

## Report

```
App:        <app>    Cluster: <cluster>
Revision:   <before> → <after>
Diff shown: yes — <n> changes, of which <m> were not the user's
Sync:       <phase> — <message>
Workload:   <verified by kubernetes-agent: pods ready | not verified>
Pruned:     no | <resources deleted>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Syncing without showing the diff | Other changes ride along |
| Syncing a pinned app and reporting success | The pin must move |
| `--prune` by default | Separate approval with the list shown |
| Retrying a failed sync unchanged | Read the message first |
| "Sync succeeded" as verification | Confirm pods went ready |
| Several apps on one approval | One app, one approval |
