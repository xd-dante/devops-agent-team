# Action — Bootstrap Project

No profile exists for the key. Build one from live metadata, use it for this
run, and offer to save it locally.

## Step 1 — Confirm the project exists

Call the tracker's visible-projects endpoint. Not visible → stop and report;
the key is wrong or the user lacks access.

## Step 2 — Issue types

Call the project's issue-type metadata endpoint. Record each type's name and
id.

## Step 3 — Fields per issue type

For each issue type, call the create-field metadata endpoint with
`requiredFieldsOnly: false`. Record:

| Need | Where it shows up |
|------|-------------------|
| Components | `components.allowedValues` |
| Sprint, team, story points, acceptance-criteria field | Custom fields, matched by **schema type and name**, never by id guess |
| Whether sprint applies | Sprint field present on the type's create screen |
| Fields the screen rejects | Absent from the create metadata — candidate `omit` rules |

## Step 4 — Site and cloud id

The tracker's accessible-resources endpoint.

## Step 5 — Build the profile in memory

Same schema as `standards/project-profile.md`. Set `verified` to today. Leave
`repo_hints` for the user to confirm. Then continue in
`actions/resolve-project.md` from Step 3 — do not skip the live lookups or
field rules because the profile is new.

## Step 6 — Offer it for saving

Print the complete profile and ask:

```
No profile for <KEY>. Built one from live metadata (below).
Save it to <local profile dir>/<KEY>.yml so the next run skips these lookups?
```

Write it **only on a yes**, and only to the local profile directory. Never
into the repository being worked on, and never into this toolkit — a profile
holds site ids that are not this toolkit's business.

## Drift (stale or failing profile)

When a loaded profile is past 180 days, or the create call fails on an
unknown field or invalid value:

1. Re-run Steps 2–3 **scoped to what failed**
2. Diff live against the profile; use live values for this run
3. Report exactly what drifted and offer to update the local profile
4. Retry the create **once** with live values — never loop

Do not re-validate on every run. A live round-trip on the common path, where
nothing changed, is pure cost.

## Report

```
Bootstrapped: <KEY> — <name> on <site>
Issue types:  <n>   Components: <n>   Custom fields mapped: <list>
Unmapped:     <anything not identified — asked, not guessed>
Saved:        <path | declined | not offered>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Guessing a custom field id from another site | Match by schema and name on this site |
| Writing the profile without asking | Offer, write on a yes |
| Writing it into the work repo | Local profile directory only |
| Skipping live lookups for a fresh profile | Continue at resolve Step 3 |
| Retrying a failed create in a loop | One retry with live values |
