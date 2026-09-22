# GitOps Rules

## Git is the source of truth

An Application's desired state comes from a repo. Changing a live resource it
manages is temporary at best: the next sync reverts it, and the reason is
recorded nowhere.

**Never** `kubectl edit` / `patch` / `apply` a resource an Application
manages. The fix goes into the source repo.

## Never edit the Application itself either

Where Applications are created by infrastructure-as-code, a live edit to the
target revision, value files, sync policy, or annotations is reverted the next
time that code runs — and creates drift meanwhile.

Hand-patching an annotation to unblock something works, and then the next
apply silently removes it. If it is worth doing, it is worth doing in the
code that owns it.

## Allowed

```
argocd app get / diff / history / manifests / resources / logs
kubectl get / describe application -n <ns> <app> -o yaml
```

## Gated — sync

`argocd app sync` is a **mutation**. It deploys whatever the source repo
currently says, which may include other people's merged-but-unsynced work. It
requires explicit approval for that app and that run, a shown diff, and a
protected environment confirmed separately. See
`actions/sync-application.md`.

## Never

- `argocd app set` — that belongs to whatever owns the Application
- `argocd app delete`
- `argocd app rollback` without explicit approval — it makes live state
  diverge from git, which is the problem rather than the fix
- `--force` or `--replace` on a sync — they delete and recreate resources
- Toggling automated sync from the CLI
- Syncing "everything" to clear a list of out-of-sync apps

## Prune is dangerous

A sync with prune deletes live resources absent from git. On an app whose
chart or value files recently changed shape, that can remove more than
expected. Never prune without showing exactly which resources would go.
