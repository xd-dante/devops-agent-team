# Cluster Discovery

## Resolve, never construct

```bash
kubectl config get-contexts -o name
kubectl config current-context
```

A context name may be an ARN, an alias, or anything else — it often does not
match the cluster name. Pick the context whose name contains the resolved
cluster, then switch only:

```bash
kubectl config use-context <existing-context-name>
```

No match → **stop and report.** The user authenticates it. Writing a
kubeconfig is not this agent's job.

**Check `current-context` every session** — it drifts between sessions, and a
stale context is the usual reason a namespace appears to be missing.

## Echo the target before gathering

```
Investigating on: <cluster>  (context: <name>)
```

Mandatory for a protected environment, useful everywhere.

## Environment mapping

From `.devops-agents.yml` `environments.<env>.cluster` and `cloud_profile`
where present. Otherwise ask which environment, and match it against the
context list. Never infer from a naming pattern alone.

## Ownership routing — where a fix actually lands

The cluster is a **read** surface; desired state lives in git. A pod spec
that looks wrong is a chart or infrastructure finding.

| Finding | Owner |
|---------|-------|
| Resources/limits, probes, env vars, replicas | `helm-agent` → chart values |
| Wrong image version | `kargo-agent` → promotion |
| Not synced, drifted, pinned revision | `argocd-agent` |
| Node pools, autoscaling, cluster add-ons | `terraform-agent` |
| Network policy, identity bindings, secrets wiring | `terraform-agent` |
| Managed database, network, quota behaviour | `aws-investigator-agent` |

A finding with no owner named is unfinished work.

## Recurring traps

- `runAsNonRoot: true` **alone** fails when the image's `USER` is a name
  rather than a numeric uid — the kubelet cannot verify it. A numeric
  `runAsUser` is required.
- A chart can override an image's own security context, so a correctly
  non-root image still fails. Check the **rendered spec**, not the Dockerfile.
- Pods reaching cloud services may have their own network identity (a
  dedicated interface with its own security group), in which case node-level
  rules do not apply to them.
- `kubectl` may not be the binary you expect — verify before concluding a
  cluster is unreachable.
