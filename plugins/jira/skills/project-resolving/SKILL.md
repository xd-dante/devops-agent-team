---
name: project-resolving
description: 'Resolve everything project-specific about an issue-tracker project before a ticket is created — site and cloud id, project key, board, custom field ids, issue types, components, team ids, and per-project quirks — from a local project profile plus a few live lookups. Resolves only, never creates or edits. Use when a ticket is about to be written, when asked which project a repo belongs to, or what fields a project uses.'
---

# Project Resolving

Turns "create a ticket" into a **call-ready create payload** with three holes
left: summary, description, parent. Everything else — ids, components,
sprint, team, quirks — is resolved here, so the writing skill stays generic
across projects.

**Resolves only.** It never creates or edits an issue. It hands back an
envelope; `ticket-writing` fills it and sends it.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Resolve Project | `actions/resolve-project.md` | Key → profile → live lookups → field rules → envelope |
| Bootstrap Project | `actions/bootstrap-project.md` | No profile for the key: build one from live metadata, offer it for local save |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Project Profile | `standards/project-profile.md` | Where profiles live, the schema, what may and may not be cached |
| Field Rules | `standards/field-rules.md` | `omit` / `top_level` quirks, applied mechanically |
| Checklist | `standards/checklist.md` | Pre-handoff checks |

## Principles

1. **Static facts from the profile, volatile facts live** — field ids are
   cached; sprints, account ids and epics never are.
2. **An inferred key is confirmed** — never act on a guessed project.
3. **Quirks are applied, not interpreted** — a rule's `action` is literal.
4. **Never invent an id** — a missing value is re-fetched or asked for.
5. **The envelope is sendable** — the caller fills holes, it does not decode
   field ids.

## Usage

1. Load this manifest and `standards/project-profile.md`.
2. Profile found for the key → `actions/resolve-project.md`.
3. No profile → `actions/bootstrap-project.md`, then continue in
   `resolve-project.md` from the live lookups.
4. Validate against `standards/checklist.md` before handing back.
