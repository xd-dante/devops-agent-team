# Action — Create Ticket

Create a ticket when work needs one and none exists. Called by the
orchestrator's delivery flow whenever no ticket id was supplied.

## Step 1 — Check for a duplicate first

The most valuable step. Search on the **subject noun**, not the phrasing of
the request — an existing ticket is titled in 2–5 words and will not match a
sentence.

Found one → report it and stop. Do not create a second ticket for tracked
work.

## Step 2 — Discover, do not hardcode

Per `standards/field-discovery.md`: site id, project id, issue types, custom
field ids, active sprint, and the current user are all resolved at runtime.
Re-query the active sprint every time — sprints roll.

## Step 3 — Gather input

Infer from the request where possible. Ask once, together, for what is
genuinely missing:

| Field | Default |
|-------|---------|
| Summary | — (required, 2–5 words, no leading verb) |
| Type | The project's default work type |
| Description | What and why, 1–3 short paragraphs |
| Acceptance criteria | Ask if the outcome is not obvious |
| Parent | None |
| Priority | The project's middle value |

Do **not** ask about reporter, assignee, team or sprint — those are defaults.
Never ask for anything discoverable.

## Step 4 — Create, then read back

Create the issue, then read it back to confirm the fields landed — custom
fields silently drop when an id is wrong.

## Report

```
Created:  <KEY> — <summary>
URL:      <tracker-url>/browse/<KEY>
Type:     <type>   Priority: <priority>   Sprint: <sprint>
Assignee: <current user>
Criteria: <as set>
Duplicate check: <searched "<terms>" — none found | found <KEY>>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Creating without a duplicate search | Search the subject noun first |
| Hardcoding a field or board id | Discover it; ids differ per instance |
| A sentence-shaped title | 2–5 words, no leading verb |
| Asking for the assignee or sprint | Defaults — do not ask |
| Implementation plan in the description | The ticket states the problem |
| Not reading the issue back | Custom fields drop silently on a bad id |
| One omnibus ticket with a checklist | One ticket per actionable item |
