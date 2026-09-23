# Ticket Conventions

## Titles — 2–5 words, no leading verb, ~50 char ceiling

A title names the subject. The issue type carries the verb.

```
✅  Promotion pipeline dedup
✅  Production runner images
✅  API server alerting
✅  Connection pool evaluation

🚫  Add deduplication for the promotion pipeline so we stop copy-pasting
🚫  Investigate why the stage shows unhealthy
🚫  Fix the thing with the runners
```

Short titles stay greppable and scannable in a board view. Detail belongs in
the description.

## Descriptions

- What and why, in one to three short paragraphs
- Current behaviour, then desired behaviour
- Links to the repos and files involved
- Acceptance criteria in the **acceptance-criteria field**, not buried in
  prose

Do not write the implementation plan into the ticket. The ticket states the
problem; the PR states the solution.

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
