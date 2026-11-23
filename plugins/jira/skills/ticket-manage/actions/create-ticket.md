# Action — Create Ticket

Create a ticket when work needs one and none exists. Called by the
orchestrator's delivery flow whenever no ticket id was supplied.

Creation is owned by the **`ticket-writing`** skill, which gets every
project-specific value from **`project-resolving`**. This action is the entry
point; it does not restate their rules.

## Step 1 — Check for a duplicate first

Search on the **subject noun**, not the phrasing of the request — an existing
ticket is titled in 2–5 words and will not match a sentence. Use
`actions/search-tickets.md`.

Clearly tracked already → report it and stop. Possibly related → carry the
hits into the review gate; the user decides.

## Step 2 — Draft and gate

Run `ticket-writing` → `actions/draft-ticket.md`. It resolves the project,
drafts title, description and criteria, and stops at the review gate.

Dispatched as a subagent → return the draft with `Status: awaiting approval`.
Do not create.

## Step 3 — Create on approval

Only with the approved draft in hand: `ticket-writing` →
`actions/create-approved.md`. It sends the resolved envelope and reads the
issue back.

## Report

`ticket-writing`'s report: the draft while awaiting approval, or the
`Created:` block once created.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Creating without a duplicate search | Search the subject noun first |
| Restating title or field rules here | They live in `ticket-writing` and `project-resolving` |
| Creating before the draft is approved | Stop at the review gate |
| Hardcoding a field, board or component | `project-resolving` supplies them |
| One omnibus ticket with a checklist | One ticket per actionable item |
