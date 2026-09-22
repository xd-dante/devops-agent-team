# Action — Revision Pin

"It says synced, but my merged change is not deployed." The usual answer is a
pinned target revision.

## Why this happens

| `targetRevision` | Behaviour |
|------------------|-----------|
| `HEAD` or a branch name | Tracks the branch — a merge is picked up on the next sync |
| a commit sha | **Pinned.** New commits on the branch are invisible |
| a tag or chart version | **Pinned** to that version |

A pinned app is legitimately "synced" — it matches the revision it was told
to track. Nothing is broken; the pin has to move.

Promotion tooling adds a second mechanism: it can pin the revision to the
exact promoted commit, deliberately, so that a floating branch head does not
race ahead when another app promotes on the same branch. If an app's revision
keeps changing under you, that is why.

## Step 1 — Confirm the pin

```bash
kubectl get application -n <ns> <app> -o jsonpath='targetRevision={.spec.source.targetRevision}{"\n"}syncedRevision={.status.sync.revision}{"\n"}'
```

A sha or version rather than a branch means pinned. Then check whether your
commit is even included:

```bash
git -C <chart-repo> fetch
git -C <chart-repo> merge-base --is-ancestor <your-commit> <pinned-sha> \
  && echo included || echo "NOT included"
```

## Step 2 — Find who sets it

```bash
grep -rn "target_revision\|targetRevision" <infra-repo>/ 2>/dev/null
```

It is owned by whatever generates the Application — not something to patch on
the live object.

## Step 3 — Route the fix

| Situation | Fix | Owner |
|-----------|-----|-------|
| The pin should move to the new commit or version | Update it in the module call or environment values, then a targeted apply | `terraform-agent` |
| The app should track the branch instead | Change it to the branch — **with the reason stated**, since pins usually exist deliberately | `terraform-agent` |
| Promotion tooling manages the pin | Promote instead of editing code | `kargo-agent` |

**Do not** `argocd app set --revision`. It is reverted by the next apply and
creates drift meanwhile.

## Report

```
App:             <app>    Cluster: <cluster>
targetRevision:  <value>   (pinned: yes)
Your commit:     <sha> — included in the pinned revision: no
Consequence:     merging alone deploys nothing for this app
Fix:             move the pin in <repo>/<file>, then a targeted apply
Owner:           terraform-agent (or kargo-agent if promotion manages it)
Nothing was synced or mutated.
```

Say the consequence plainly. This is where users are most often misled.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Concluding "synced means deployed" | Synced means matching the target revision, which may be a pin |
| `argocd app set --revision` | The owning code is reverted over it |
| Removing a pin without asking | Pins are usually deliberate |
| Missing that promotion tooling owns the pin | Promote instead of editing |
| "Just merge and it deploys" | For a pinned app, say the pin must move |
