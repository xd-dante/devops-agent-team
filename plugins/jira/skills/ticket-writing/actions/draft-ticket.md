# Action — Draft Ticket

From a request to an approved draft. Nothing is created in this action.

## Step 1 — Resolve the project

Run `project-resolving` first, passing the issue type if known. Keep its
envelope — `content_constraints`, `epic_candidates`, `notes`, `create_call` —
for the rest of the flow. Resolution failed → **stop and ask**; never guess a
cloud id, field id or component to work around it.

Issue type not stated → ask. It decides the title rules.

## Step 2 — Title

Per `standards/title-rules.md`. Start with a component from
`content_constraints.components`, or the partner or system name when none
fits. Never invent a component.

## Step 3 — Description

Per `standards/body-format.md`: one paragraph, persona or situation first,
then what changes and why.

## Step 4 — Acceptance criteria

Only when `content_constraints.acceptance_criteria` is `true` for the type.
3–7 lines, each `The <subject> shall <observable behaviour> <threshold>. (P1–P10)`.
More than 7 → propose a split instead.

## Step 5 — Open questions

Only real unknowns: an assumption made to keep drafting, an unconfirmed
dependency. None → omit the section. Do not manufacture questions.

## Step 6 — Duplicate check

Take 2–3 significant nouns from the title. Run
`content_constraints.duplicate_search_jql_template` with `maxResults: 5`,
fields `summary`, `status`, `assignee`. Hits go **into** the review gate.
Never abort on a match.

## Step 7 — Review gate

Print the whole draft and ask:

```
Draft — <type> in <KEY>
Title:       <title>
Parent:      <key | none | candidates: …>

<assembled markdown body>

Similar open tickets: <KEY — summary — status>, … | none found
Notes: <envelope notes>

Create this, revise it, comment on an existing ticket instead, or stop?
```

Changes requested → revise, re-print the **whole** draft, ask again.

**Dispatched as a subagent** (no user to ask) → return the draft as the
report with `Status: awaiting approval` and stop. The orchestrator shows it to
the user; creation happens only when a later brief carries the approved draft
verbatim.

## Report

The review-gate block above, plus `Status: awaiting approval | approved | stopped`.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Drafting before resolving the project | The title needs the component list |
| Inventing a component | Use the resolved list or the partner name |
| Multi-paragraph or implementation-heavy body | One paragraph, problem and outcome |
| Criteria on an Epic | Criteria belong on its children |
| Aborting on a duplicate hit | Surface it in the gate; the user decides |
| Creating from a subagent without approval | Return the draft, status awaiting approval |
| Re-printing only the changed part | Re-print the whole draft every round |
