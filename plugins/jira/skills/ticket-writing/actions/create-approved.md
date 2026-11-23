# Action — Create Approved Ticket

## Gate — all required
- [ ] The user approved **this exact draft** — title, body, parent
- [ ] The full draft was printed at the review gate, after the last revision
- [ ] The project resolved; the envelope is from this run
Any box unticked → 🛑 STOP.

## Step 1 — Fill the envelope

Take `create_call` from the `project-resolving` envelope and fill its holes:

| Hole | Value |
|------|-------|
| `summary` | The approved title |
| `description` | The assembled markdown from `standards/body-format.md` |
| `parent` | The confirmed parent, or drop the key when none |

Drop any other unfilled optional field. Send the call **as resolved** — do not
re-derive or override cloud id, sprint, team, priority or custom fields.

## Step 2 — Handle a failure once

Unknown field or invalid value → hand back to `project-resolving`'s drift
path, then retry **once** with the live values. A second failure → stop and
report the error verbatim.

## Step 3 — Read it back

Fetch the created issue. Confirm the summary, type, sprint, team and parent
landed — a wrong custom field id drops silently.

## Report

```
Created:   <KEY> — <summary>
URL:       <site>/browse/<KEY>
Type:      <type>   Priority: <priority>   Sprint: <sprint | n/a>
Parent:    <key | none>
Assignee:  <resolved user>
Read back: <all fields landed | <field> missing>
Notes:     <envelope notes, e.g. reporter must be set in the UI>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Creating before approval | The gate is the point |
| Overriding a resolved value | Send the envelope as resolved |
| Criteria put in the acceptance-criteria custom field | They live in the markdown body |
| Retrying in a loop | One retry with live values |
| Skipping the read-back | Bad field ids drop without an error |
| Dropping the envelope notes | Print them with the result |
