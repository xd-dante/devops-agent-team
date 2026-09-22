# Investigation Checklist

## Before gathering
- [ ] Environment established explicitly
- [ ] Cluster resolved to an **existing** context, not a constructed name
- [ ] `current-context` checked — it drifts between sessions
- [ ] Active cluster echoed back to the user

## Gathering
- [ ] Read verbs only
- [ ] Evidence captured verbatim: events, statuses, exit reasons, log lines
- [ ] `--previous` logs read on anything that restarted
- [ ] `lastState.terminated.reason` read, not inferred
- [ ] Rendered spec inspected rather than chart source or Dockerfile

## Reasoning
- [ ] Symptom separated from root cause
- [ ] Time correlation checked — what changed just before it broke
- [ ] Hypotheses ranked and labelled when unproven
- [ ] Managed-by established: which repo owns desired state

## Reporting
- [ ] Cluster and context named at the top
- [ ] Every finding carries its evidence
- [ ] Fix stated as a recommendation with the owning route
- [ ] Explicit statement that nothing was mutated
- [ ] Any command the human must run surfaced verbatim
