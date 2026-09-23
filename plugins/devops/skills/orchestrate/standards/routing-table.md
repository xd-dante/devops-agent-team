# Routing Table

The dispatch contract. A domain is resolved here, not from intuition.

> An agent absent from this table is never dispatched, however good its own
> description is. Adding an agent means adding a row.

## Domain → agent

| Signal in the request | Agent | Plugin | Hub skill |
|-----------------------|-------|--------|-----------|
| Ticket: read, create, comment, transition, search | `ticket-analyst` | `jira` | `ticket-manage` |
| Worktree, branch, commit, PR, review comments, CI | `delivery-engineer` | `github` | `pr-deliver` |
| Terraform: plan, apply, module, variable, state, workspace | `terraform-engineer` | `terraform` | `terraform-change` |
| Helm: chart templates, values, library chart, render | `helm-engineer` | `helm` | `helm-authoring` |
| Live cluster: pod crash, rollout, events, nodes, networking | `kubernetes-investigator` | `kubernetes` | `k8s-triage` |
| GitOps: Application health, sync, drift, target revision | `argocd-analyst` | `argocd` | `argocd-diagnose` |
| Promotion: Freight, Warehouse, Stage, PromotionTask | `kargo-promoter` | `kargo` | `kargo-promote` |
| Cloud resource behaviour: database, network, IAM, logs | `aws-investigator` | `aws` | `aws-investigate` |
| Cloud money: cost, spend, bill, rightsizing, savings | `aws-cost-analyzer` | `aws` | `aws-cost-analysis` |
| Observability: is anything wrong, daily check, alert coverage, dashboards | `newrelic-analyst` | `newrelic` | `newrelic-triage` |

## Disambiguation

These pairs get confused. Resolve with the rule, not a guess.

| Looks like both | Route to | Because |
|-----------------|----------|---------|
| "pod unhealthy" + "app shows Degraded" | `kubernetes-investigator`, then `argocd-analyst` | Pod evidence explains the app status; the reverse rarely holds |
| "running the wrong version" | `kargo-promoter` | Version movement is a promotion concern before a sync or chart one |
| "synced but nothing changed" | `argocd-analyst` | Usually a pinned target revision |
| "chart value not taking effect" | `helm-engineer` + `terraform-engineer` | Classify the value as static or computed first |
| "node count / autoscaling" | `kubernetes-investigator` | Read from the cluster; the fix lands in Terraform |
| "the database is slow" | `aws-investigator` | Engine and instance behaviour |
| "the database is expensive" | `aws-cost-analyzer` | Money questions always go to cost, same resource or not |
| "is anything broken?" with no service named | `newrelic-analyst` | Start from the monitoring verdict; it names which service to dig into |
| "why is `<service>` slow" | `newrelic-analyst`, then the owner it routes to | Golden signals say *which* kind of slow, which decides the next agent |
| "we got paged, what happened" | `newrelic-analyst` | It holds the issue and deploy timeline; the cluster agent holds the pod evidence |
| "add an env var to a service" | `helm-engineer` + `terraform-engineer` | Static vs computed decides the owner |

## Cross-cutting: memory

`memory` is a **skill every agent uses**, not a dispatch target. There is no
memory agent, and nothing is routed to one.

| Signal | Load |
|--------|------|
| Start of any task | `remember/actions/recall.md` — standing instructions and relevant entries |
| "keep in mind", "save this", "from now on", "always", "never" | `remember/actions/remember.md` |
| The user corrected you, or you rediscovered something expensive | `remember/actions/suggest.md` — **offer**, never save silently |
| "forget that", or an entry contradicts reality | `remember/actions/forget.md` |

Memory is local and gitignored. Never quote it into a commit, PR, or public
document.

## Fan-out sets

| Request shape | Set |
|---------------|-----|
| Ticket delivery | `ticket-analyst` → domain specialists → `delivery-engineer` |
| "X is down in \<env\>" | `newrelic-analyst` for the timeline, plus `kubernetes-investigator` + `argocd-analyst` + `aws-investigator` in parallel, then one root cause |
| Daily / morning check | `newrelic-analyst` alone — it escalates only what it finds |
| Deploy not arriving | `kargo-promoter` + `argocd-analyst` |
| Cost review | `aws-cost-analyzer`, then `terraform-engineer` for the fix |
| Value change across repos | `helm-engineer` + `terraform-engineer`, ordered by dependency |

## Preflight

A specialist exists only if its plugin is enabled. Before dispatching:

1. Check the agent is in the available agent list.
2. Missing → **do not substitute a nearby specialist.** Either invoke that
   plugin's hub skill directly and do the work in your own context, or stop
   and report which plugin to enable.
3. Say in the report which path was taken. Never let the user believe a
   specialist ran when it did not.

## Not routed here

- Application business logic — no specialist owns it; hand back to the user.
- Anything needing credentials the session does not have.
- Any mutation the owning agent's own boundaries forbid. You cannot grant a
  specialist permission its skill denies it.
