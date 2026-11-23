---
name: ticket-writing
description: 'Write an issue-tracker ticket (Story, Bug, Task, Support, Epic) where the wording matters — a type-appropriate title, a one-paragraph description, testable acceptance criteria, a duplicate check, and an explicit review gate before anything is created. Works for any project; project metadata comes from project-resolving. Use when asked to write, draft, file or create a story, bug, task or epic, or to turn something into a ticket.'
---

# Ticket Writing

Owns **authoring quality and the create call itself**. Everything
project-specific — ids, components, issue types, sprint, team, quirks —
comes from `project-resolving`, so this skill never hardcodes a project.

The defining rule: **no ticket is created without explicit approval of the
full draft.**

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Draft Ticket | `actions/draft-ticket.md` | Resolve → title → description → criteria → duplicates → review gate |
| Create Ticket | `actions/create-approved.md` | Fill the resolver's envelope with the approved draft and send it |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Title Rules | `standards/title-rules.md` | Per-type length and verb rules, component-first |
| Body Format | `standards/body-format.md` | One-paragraph description, criteria shape, assembled markdown |
| Checklist | `standards/checklist.md` | Pre-gate and pre-create checks |

## Principles

1. **Resolve first** — the title depends on the project's component list.
2. **The type decides the verb** — Story, Bug, Epic name an outcome; a Task
   names an action.
3. **One paragraph** — the problem and the outcome, never the implementation.
4. **Every criterion is pass/fail** — one assertion, one line, a weight.
5. **Duplicates inform, never abort** — the user decides.
6. **Review gate before create** — always, and again after every revision.
7. **Send the envelope as resolved** — do not second-guess its values.

## Usage

1. Load this manifest and `standards/title-rules.md`.
2. Execute `actions/draft-ticket.md` through the review gate.
3. On approval, execute `actions/create-approved.md`.
4. Validate against `standards/checklist.md`.
