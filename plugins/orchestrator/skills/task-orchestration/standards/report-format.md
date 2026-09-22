# Report Format

One report per task.

```
Task:        <the ask, restated in one line>
Routed to:   <agent> (<plugin>) [+ <agent> ...]
Environment: <env> / <cloud profile> / <cluster>

Findings
  - <fact> — <evidence: command output, file:line, resource id>

Root cause
  <best-supported explanation, or ranked hypotheses when unproven>

Done
  - <what actually changed, with paths and PR links>

Not done
  - <what was skipped or blocked, and why>

Next
  - <the specific action the user must take, if any>
```

## Rules

- **Evidence or nothing.** A claim with no command, path, or resource id
  behind it does not go in the report.
- **Name the specialist.** The user must be able to see who found what.
- **"Not done" is mandatory when non-empty.** Blocked, skipped and
  out-of-scope items get stated. Scaling the work down is the user's call.
- **Links inline.** Every PR gets its URL on first mention, plus a recap of
  every PR opened in the session.
- **Label hypotheses.** If a root cause is unproven, say so and give the
  check that would confirm it.
- **Say whether anything was mutated.** "Investigated only, nothing changed"
  is a useful sentence.
