---
name: k8s-triage
description: 'Investigate and triage Kubernetes workloads — crashing pods, stuck rollouts, unreachable services, unschedulable pods, node and autoscaler capacity — and route the fix to the repo that owns desired state. Use when asked why a pod, deployment, service, ingress or node is misbehaving in an environment. Read-only apart from one explicitly gated ephemeral debug container action.'
allowed-tools: Bash
---

# Kubernetes Operations

Cluster-side investigation: gather evidence, name a root cause, route the fix
to whoever owns desired state.

**Read-only by default.** The cluster is a read surface — desired state lives
in git, so a pod spec that looks wrong is a chart or infrastructure finding,
not something to patch in place. Exactly one action mutates, and it is gated.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Triage Workload | `actions/triage-workload.md` | Crashing, restarting, failing pods — classify from evidence |
| Inspect Rollout | `actions/inspect-rollout.md` | Stuck deployments, versions that never went live |
| Check Networking | `actions/check-networking.md` | Services, endpoints, ports, mesh, egress identity |
| Node Capacity | `actions/node-capacity.md` | Pending pods, pressure, autoscaler behaviour |
| Ephemeral Debug Container | `actions/ephemeral-debug-container.md` | **Gated, mutating.** Reach a dependency from a pod's network identity |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Read-Only Rules | `standards/read-only-rules.md` | Allowed and forbidden verbs, red flags |
| Cluster Discovery | `standards/cluster-discovery.md` | Resolve contexts, environment mapping, ownership routing, recurring traps |
| Checklist | `standards/checklist.md` | Pre-report checks |

## Principles

1. **Read-only, always** — `exec`, `port-forward` and `debug` count as
   mutating; they open sessions that can change state.
2. **Switch contexts, never create them** — the cluster is already
   authenticated.
3. **Echo the target before gathering** — context drifts between sessions.
4. **Evidence verbatim** — scheduling messages and terminated reasons are
   precise. Quote them.
5. **Symptom is not root cause** — OOMKilled is a symptom; the limit is the
   cause.
6. **Every finding has an owner** — a finding without a route is unfinished.

## Usage

1. Load this manifest and `standards/read-only-rules.md`.
2. Resolve and echo the target cluster per `standards/cluster-discovery.md`.
3. Execute the symptom's action file.
4. Validate against `standards/checklist.md`.
