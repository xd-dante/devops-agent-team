# Routing Table

The dispatch contract. A domain is resolved here, not from intuition.

> An agent absent from this table is never dispatched, however good its own
> description is. Adding an agent means adding a row.

## Domain → agent

| Signal in the request | Agent | Plugin | Hub skill |
|-----------------------|-------|--------|-----------|
| Ticket: read, create, comment, transition, search | `jira-agent` | `jira` | `jira-workflow` |
| Worktree, branch, commit, PR, review comments, CI | `github-agent` | `github` | `github-delivery` |
| Terraform: plan, apply, module, variable, state, workspace | `terraform-agent` | `terraform` | `terraform-workflow` |
| Helm: chart templates, values, library chart, render | `helm-agent` | `helm` | `helm-charts` |
| Live cluster: pod crash, rollout, events, nodes, networking | `kubernetes-agent` | `kubernetes` | `k8s-operations` |
| GitOps: Application health, sync, drift, target revision | `argocd-agent` | `argocd` | `argocd-operations` |
| Promotion: Freight, Warehouse, Stage, PromotionTask | `kargo-agent` | `kargo` | `kargo-pipelines` |
| Cloud resource behaviour: database, network, IAM, logs | `aws-investigator-agent` | `aws` | `aws-investigate` |
| Cloud money: cost, spend, bill, rightsizing, savings | `aws-cost-agent` | `aws` | `aws-cost-analysis` |

## Disambiguation

These pairs get confused. Resolve with the rule, not a guess.

| Looks like both | Route to | Because |
|-----------------|----------|---------|
| "pod unhealthy" + "app shows Degraded" | `kubernetes-agent`, then `argocd-agent` | Pod evidence explains the app status; the reverse rarely holds |
| "running the wrong version" | `kargo-agent` | Version movement is a promotion concern before a sync or chart one |
| "synced but nothing changed" | `argocd-agent` | Usually a pinned target revision |
| "chart value not taking effect" | `helm-agent` + `terraform-agent` | Classify the value as static or computed first |
| "node count / autoscaling" | `kubernetes-agent` | Read from the cluster; the fix lands in Terraform |
| "the database is slow" | `aws-investigator-agent` | Engine and instance behaviour |
| "the database is expensive" | `aws-cost-agent` | Money questions always go to cost, same resource or not |
| "add an env var to a service" | `helm-agent` + `terraform-agent` | Static vs computed decides the owner |

## Cross-cutting: memory

`memory` is a **skill every agent uses**, not a dispatch target. There is no
memory agent, and nothing is routed to one.

| Signal | Load |
|--------|------|
| Start of any task | `agent-memory/actions/recall.md` — standing instructions and relevant entries |
| "keep in mind", "save this", "from now on", "always", "never" | `agent-memory/actions/remember.md` |
| The user corrected you, or you rediscovered something expensive | `agent-memory/actions/suggest.md` — **offer**, never save silently |
| "forget that", or an entry contradicts reality | `agent-memory/actions/forget.md` |

Memory is local and gitignored. Never quote it into a commit, PR, or public
document.

## Fan-out sets

| Request shape | Set |
|---------------|-----|
| Ticket delivery | `jira-agent` → domain specialists → `github-agent` |
| "X is down in \<env\>" | `kubernetes-agent` + `argocd-agent` + `aws-investigator-agent` in parallel, then one root cause |
| Deploy not arriving | `kargo-agent` + `argocd-agent` |
| Cost review | `aws-cost-agent`, then `terraform-agent` for the fix |
| Value change across repos | `helm-agent` + `terraform-agent`, ordered by dependency |

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
