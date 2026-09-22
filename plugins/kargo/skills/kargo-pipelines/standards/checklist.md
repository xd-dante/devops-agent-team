# Promotion Checklist

## Before diagnosing
- [ ] Environment and cluster established; context echoed
- [ ] Project namespace identified
- [ ] The app's chart shape known — it decides the image tag key

## Diagnosing a promotion
- [ ] **Per-step** phases read, not just the overall phase — a succeeded
      promotion can contain skipped steps
- [ ] Skipped steps checked against their condition
- [ ] Expression scope verified: `task.outputs[...]` inside a task
- [ ] The image tag key confirmed to exist in the values file
- [ ] "No diff" ruled in or out before blaming configuration

## Before promoting
- [ ] User approved this app, this Stage, and this run
- [ ] Freight identified explicitly, with its tag
- [ ] Whether it is a real version change or a same-version no-op is stated
- [ ] Downstream effect understood — which environment actually redeploys
- [ ] Protected environments confirmed separately

## Pipeline config changes
- [ ] Only one pipelines chart edited
- [ ] Renders diffed **semantically** — parse and key by
      `(kind, name, namespace)`, not raw line diff
- [ ] Tag filters understood as pipeline-wide
- [ ] Secret templates checked against live state before merge
- [ ] The owning Application must be synced after merge, or the new task
      never lands

## Reporting
- [ ] Freight, Stage, tag and per-step outcome stated
- [ ] Root cause distinguished from "the promotion succeeded"
- [ ] Fix routed to the owning repo and agent
- [ ] Explicit statement of whether anything was promoted
