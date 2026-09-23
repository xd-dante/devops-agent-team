---
name: ticket-manage
description: 'Work with issue-tracker tickets — read full ticket context including attachments before implementing, create a ticket when none exists, record outcomes with their reasoning, and search for duplicates or prior work. Use when a ticket id appears in a request, when someone asks what a ticket wants, when work needs a ticket, or when a ticket needs updating or closing.'
---

# Ticket Workflow

Ticket-side work: understanding what a ticket actually asks for, creating one
when work has none, recording outcomes, and finding prior work.

The defining rule: **a title is not a specification.** Titles are 2–5 words;
the requirement usually lives in the acceptance-criteria field, an
attachment, or the last comment.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Read Ticket | `actions/read-ticket.md` | Description, criteria, **attachments**, comments, links, affected repos |
| Create Ticket | `actions/create-ticket.md` | Duplicate check, discovered field ids, sane defaults |
| Update Ticket | `actions/update-ticket.md` | Comment with the reasoning, then transition |
| Search Tickets | `actions/search-tickets.md` | Duplicates, prior work, roundups |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Ticket Conventions | `standards/ticket-conventions.md` | Title rules, description shape, cross-references |
| Field Discovery | `standards/field-discovery.md` | Resolve site, project, board and custom field ids at runtime |
| Checklist | `standards/checklist.md` | Reading, creating, updating and reporting checks |

## Principles

1. **Read the attachments** — they regularly carry the real requirement.
2. **Read the comments to the end** — the last one often changed the plan.
3. **Restate scope before implementing** — the cheapest misread-catcher.
4. **Titles name subjects** — 2–5 words, no leading verb.
5. **Reasoning before status** — a transition without a comment is a dead end.
6. **Discover ids, never hardcode** — they differ per instance and change.
7. **Never invent to fill a gap** — an ambiguous ticket gets a question.
8. **One ticket per actionable item.**

## Usage

1. Load this manifest and `standards/ticket-conventions.md`.
2. Resolve tracker facts per `standards/field-discovery.md`.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md`.
