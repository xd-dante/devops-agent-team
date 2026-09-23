# Memory

Agents in this toolkit persist facts about **your** environment so they stop
re-deriving them and stop repeating corrections you have already made.

That material — cluster names, account ids, tracker hostnames, your
preferences — is precisely what this public repo must never contain. So
memory lives in a **local, gitignored** directory.

## Where it lives

Resolution order, first match wins:

| Order | Location | Use |
|-------|----------|-----|
| 1 | `$DEVOPS_AGENT_MEMORY` | Explicit override |
| 2 | `<project-root>/.devops-agents/memory/` | Project-scoped — facts about this codebase |
| 3 | `~/.devops-agents/memory/` | Global — facts true across all your work |

Project scope wins for reads; a fact is written to whichever scope it is true
in. "This repo bases on `develop`" is project scope. "Always use targeted
applies" is global.

## Layout

```
<memory-dir>/
  MEMORY.md            index — one line per entry, loaded first
  instructions.md      your standing instructions — always loaded, freeform
  entries/<slug>.md    one fact per file
```

## Getting started

```bash
mkdir -p ~/.devops-agents/memory/entries
cp memory/MEMORY.md.example       ~/.devops-agents/memory/MEMORY.md
cp memory/instructions.md.example ~/.devops-agents/memory/instructions.md
```

For a project-scoped directory, do the same under
`<project-root>/.devops-agents/memory/` — and **add
`.devops-agents/` to that project's `.gitignore`.**

## `instructions.md` — your own rules

A freeform file, always loaded, never summarised away. Put standing
instructions here that are not really facts:

```markdown
# Standing instructions

- Never touch production without me saying "production" explicitly.
- Open PRs against `develop` in the chart repos.
- I want plan output pasted in full, not summarised.
- Prefer smaller, single-purpose PRs over one large one.
```

Agents treat this as user instruction, which outranks their own defaults.

## Entries

One fact per file, so entries can be added, corrected and deleted
independently:

```markdown
---
name: targeted-applies-only
description: Always use -target on plan and apply in the shared infra repo
type: preference
scope: global
created: 2026-09-22
---

Never run an untargeted plan or apply in the shared infrastructure repo.

**Why:** several people have changes in flight in that state at once, so an
untargeted apply can ship someone else's half-finished work.

**How to apply:** always `-target` per intended address; if the change cannot
be expressed as a clean target set, stop and report the addresses instead of
widening.
```

`type` is one of `preference`, `convention`, `environment`, `incident`,
`reference` — see
`plugins/memory/skills/remember/standards/what-to-remember.md`.

## How agents use it

| Trigger | Behaviour |
|---------|-----------|
| Start of a task | Load `MEMORY.md` + `instructions.md`, then only the entries whose descriptions look relevant |
| "keep in mind", "remember this", "save this", "don't do that again" | Write an entry (`actions/remember.md`) |
| A correction, or the same question twice | **Offer** to save an entry — never save silently (`actions/suggest.md`) |
| A memory turns out to be wrong | Correct or delete it (`actions/forget.md`) |

## Privacy

Memory is local. Agents never quote it into a commit message, PR body,
public document, or a file in this repo. A lesson from memory can be
**generalised** into a rule here — mechanism and consequence kept, identifier
dropped — but the raw entry stays local.
