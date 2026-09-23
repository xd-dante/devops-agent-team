# Privacy Rules

Memory holds exactly the material this toolkit's own repository must never
contain. That asymmetry is the point, and it only works if the boundary is
respected in one direction.

## Never leaves the machine

A memory entry, or anything quoted from one, must not appear in:

- a commit message or commit body
- a PR title, body, or review comment
- a file in this toolkit's repository
- a ticket, document, or message to a third party
- a log or transcript shared outside the session

## The one legitimate path outward

A **lesson** from memory may become a generic rule in this toolkit — with the
identifier removed:

```
memory entry (local)
  "The chart repo bases on develop even though origin/HEAD says main.
   Four PRs merged against the wrong branch before we caught it."

        ↓ generalise: keep mechanism + consequence, drop the identifier

toolkit rule (public)
  "Probe origin/develop rather than trusting the remote's advertised
   default. A stale default silently targets PRs at the wrong branch."
```

If the rule stops making sense once the identifier is gone, it has been
redacted rather than generalised. Leave it in memory.

## Secrets

- Never store a credential **value** — record where it lives, not what it is
- Never store a full log or config dump "for context"; store the conclusion
- If the user pastes a secret and asks you to remember it, remember its
  **location** and say that is what you stored

## Gitignore hygiene

A project-scoped memory directory sits inside someone's repository, so it can
be committed by accident.

When creating one, add `.devops-agents/` to that project's `.gitignore` in
the same step, and say you did. Do not create a project memory directory in a
repo whose `.gitignore` you cannot write — use global scope instead and
explain why.
