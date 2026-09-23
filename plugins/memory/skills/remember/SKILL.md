---
name: remember
description: 'Persist and recall facts about the user and their environment in a local, gitignored memory directory — load standing instructions and relevant entries at the start of a task, save a fact when the user says to keep it in mind, offer to save one after a correction, and correct or delete an entry that has gone wrong. Use when the user says remember, keep in mind, save this, note that, from now on, always, never, or forget that; and at the start of any task, to load what is already known.'
allowed-tools: Bash
---

# Agent Memory

Agents re-deriving the same facts, and users repeating the same corrections,
are the two costs this removes.

Memory lives in a **local, gitignored** directory — it holds exactly the
site-specific material this public toolkit must never contain. That
asymmetry is the design.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Recall | `actions/recall.md` | At task start: load standing instructions and the relevant entries |
| Remember | `actions/remember.md` | Save a fact when the user says to |
| Suggest | `actions/suggest.md` | Self-learning: **offer** to save after a correction or a rediscovery |
| Forget | `actions/forget.md` | Correct or delete an entry that has gone wrong |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Memory Layout | `standards/memory-layout.md` | Resolution order, entry format, index lines, writing rules |
| What to Remember | `standards/what-to-remember.md` | Types, scope, what does not qualify, staleness |
| Privacy Rules | `standards/privacy-rules.md` | Never leaves the machine; the one legitimate path outward |
| Checklist | `standards/checklist.md` | Per-capability checks |

## Principles

1. **Offer, never save silently** — memory shapes future behaviour, so the
   user decides what goes in.
2. **`instructions.md` is user instruction** — it outranks agent defaults.
3. **One fact per file** — so it can be corrected or deleted independently.
4. **`**Why:**` is mandatory** — an entry without its reasoning gets ignored
   or argued with later.
5. **Verify before acting** — an entry records what was true when written.
6. **A wrong entry is worse than none** — correct it rather than working
   around it.
7. **Never leaves the machine** — not into a commit, a PR, a doc, or this
   repo. A *lesson* may be generalised into a rule; the entry stays local.
8. **Optional by design** — no memory directory is not an error.

## Usage

1. `actions/recall.md` at the start of a task, before planning.
2. `actions/remember.md` when the user asks.
3. `actions/suggest.md` at a pause when something accrued.
4. `actions/forget.md` when an entry has gone wrong.
5. Validate against `standards/checklist.md`.

Setup instructions for a first-time memory directory: `memory/README.md` at
the repository root.
