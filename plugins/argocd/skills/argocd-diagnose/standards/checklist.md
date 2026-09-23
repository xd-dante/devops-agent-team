# GitOps Checklist

## Before diagnosing
- [ ] Environment and cluster established; context echoed
- [ ] The app's owning repo identified
- [ ] Automated sync checked — off changes what "out of sync" means
- [ ] Value path classified: static (`valueFiles`) vs computed

## Diagnosing
- [ ] `sync.status`, `health.status`, revision **and** `operationState` all read
- [ ] `targetRevision` checked for a pin before concluding "synced but old"
- [ ] The actual diff inspected, not inferred from status
- [ ] Resource-level health read for a degraded app, then routed for the
      pod-level cause

## Before syncing
- [ ] User approved this app and this run explicitly
- [ ] The diff was shown first
- [ ] Other people's merged-but-unsynced changes surfaced
- [ ] Prune off, or the exact resources to be deleted shown
- [ ] Protected environment confirmed separately

## Reporting
- [ ] Cluster, app, revision and status stated
- [ ] Root cause distinguished from status text
- [ ] Fix routed to the owning repo and agent
- [ ] Explicit statement of whether anything was synced
