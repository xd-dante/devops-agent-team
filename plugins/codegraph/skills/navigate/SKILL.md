---
name: navigate
description: 'Find and understand code structurally — index a repository, produce a short orientation profile for an unfamiliar one, locate a symbol and its callers, and check the blast radius before changing shared code. Use when asked where something is used, who calls it, what a change would affect, or to get oriented in a repo. Works with a code-graph MCP server where one is connected and falls back to grep where it is not.'
allowed-tools: Bash
---

# Navigate

Structural lookup instead of guesswork: where a symbol lives, who calls it,
what a change touches, and how an unfamiliar repo is organised.

**The graph is optional.** Where a code-graph server is connected it is
preferred; where it is not, every action falls back to grep and **says so** —
because grep counts string occurrences and a graph counts resolved call
sites, and presenting one as the other overstates the confidence.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Index Repo | `actions/index-repo.md` | Build or refresh the index for a worktree; skip where a graph adds nothing |
| Profile Repo | `actions/profile-repo.md` | One-off orientation doc for an unfamiliar repo, saved to memory |
| Find Code | `actions/find-code.md` | A symbol, its callers, its importers, its tests |
| Impact Radius | `actions/impact-radius.md` | What a change touches — **before** the edit |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Graph or Grep | `standards/graph-or-grep.md` | When each is right, the degradation rule, staleness, honest reporting |
| Checklist | `standards/checklist.md` | Pre-report checks |

## Principles

1. **Never invent a tool name** — check the available list, then fall back.
2. **Index the worktree**, not the main checkout; ticket work happens in the
   worktree and the code differs subtly.
3. **Config repos do not need a call graph** — Terraform and charts are
   better served by grep. Skip, and say why.
4. **State the method** — graph with its commit, or grep. A count without a
   method is not a finding.
5. **Impact radius runs before the edit.**
6. **A graph sees one repo** — a published interface's real radius is larger.
7. **Stale is worse than slow** — note the indexed commit; refresh after a pull.
8. **Absent tests on shared code is a finding**, not a footnote.

## Usage

1. Load this manifest and `standards/graph-or-grep.md`; check server
   availability once.
2. Execute the capability's action file.
3. Validate against `standards/checklist.md`.
