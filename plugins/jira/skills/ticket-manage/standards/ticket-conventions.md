# Ticket Conventions

## Titles and descriptions

Owned by the `ticket-writing` skill: `standards/title-rules.md` (per-type
length and verb rules — a Task takes a verb, a Story does not) and
`standards/body-format.md` (one-paragraph description, weighted criteria).
Not restated here, so the two cannot drift apart.

The ticket states the problem; the PR states the solution.

## Cross-references

| Place | Format |
|-------|--------|
| Branch | `<user>/<type>/<TICKET>-<slug>` |
| Commit | `<type>: <TICKET> <description>` |
| PR title | `<type>: [<TICKET>] <2–5 words>` |
| PR body footer | `<tracker-url>/browse/<TICKET>` |

Templates are configurable — see `docs/CONFIGURATION.md`.

## Comments

- One comment per meaningful outcome, not a running log
- Conclusion first, then the evidence, then links
- Every PR referenced by URL
- A "not doing this" resolution records **why** before the transition — the
  reasoning is the deliverable

## One ticket per actionable item

Five independent changes are five tickets, not one with a checklist. Each
must be independently assignable, estimable and closeable. Use a genuine
parent relationship for hierarchy rather than a checklist in a description.
