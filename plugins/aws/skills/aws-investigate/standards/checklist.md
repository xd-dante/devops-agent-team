# Investigation Checklist

## Before reading
- [ ] Identity proved with `sts get-caller-identity`
- [ ] Profile matches the target environment
- [ ] Region explicit
- [ ] Resource identified precisely — identifier, not a guessed name
- [ ] Owning infrastructure repo identified

## Reading
- [ ] Read-only verbs only
- [ ] Time windows and resource sets scoped before expensive queries
- [ ] Evidence captured verbatim — error strings, metric values, timestamps
- [ ] Live state read rather than inferred from code

## Reasoning
- [ ] Symptom separated from root cause
- [ ] Time correlation established — what changed just before it broke
- [ ] Alternatives ruled out with evidence, not assertion
- [ ] Hypotheses labelled as hypotheses

## Reporting
- [ ] Account, profile and region stated
- [ ] Every finding carries its evidence
- [ ] Fix routed to the owning repo and agent
- [ ] Explicit statement that nothing was mutated
- [ ] No secret values in the output
