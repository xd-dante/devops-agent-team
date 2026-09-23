# Handoff Contract

How agents pass work to each other without looping or losing context.

## The block

```
HANDOFF → <agent>
objective: <one sentence, outcome-shaped>
context:   <facts already established, so it does not re-derive them>
scope:     <what it must not touch>
output:    <what to return>
```

Any agent may emit this when it finds work outside its domain. It is a
structured message, not a suggestion buried in prose.

## Two routes, deliberately asymmetric

| Kind | Route | Why |
|------|-------|-----|
| **Mutation** — change a file, resource, cluster, or repo | Back through the orchestrator | It owns sequencing and approval; agents must not chain changes between themselves |
| **Read-only question** | Peer to peer, **one hop**, and reported | Lets a GitOps agent ask a cluster agent "are the pods ready?" without a round trip |

Reads flow sideways. Writes do not. That asymmetry is the whole
loop-prevention design — there is no write depth to bound because writes
never chain.

## Rules for the receiving agent

- Treat the block as the entire context. Do not assume shared history.
- If the objective is outside your domain too, **do not pass it on** — return
  it to the orchestrator with what you learned. Two hops is a routing
  mistake, not a workflow.
- If the brief lacks the environment or a path you need, ask for it rather
  than guessing.
- Report what you did in the shape the `output` field asked for.

## Rules for the emitting agent

- Emit a handoff for out-of-domain work. Do not do it yourself because it
  "looked quick" — you would skip the standards that agent carries.
- Put the facts you already established in `context`. Re-deriving them is
  pure waste.
- Never emit a handoff that asks another agent to exceed its own boundaries.
  A read-only agent cannot be handed a mutation, whoever asks.

## Peer-consult example

```
HANDOFF → kubernetes-investigator            (read-only, one hop)
objective: confirm whether the api pods are ready in staging
context:   the Application reports Synced/Degraded; last sync 12 min ago
scope:     read-only; no cluster changes
output:    ready count, restart reasons, last terminated reason
```

The GitOps agent then reports both its own finding and the consulted answer,
naming who produced which.
