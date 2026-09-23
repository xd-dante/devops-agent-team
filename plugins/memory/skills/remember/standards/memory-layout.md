# Memory Layout

## Resolution order

First match wins for the directory; **both** scopes are read when both exist.

| Order | Location | Scope |
|-------|----------|-------|
| 1 | `$DEVOPS_AGENT_MEMORY` | Explicit override |
| 2 | `<project-root>/.devops-agents/memory/` | Project |
| 3 | `~/.devops-agents/memory/` | Global |

```bash
resolve_memory_dirs() {
  [ -n "$DEVOPS_AGENT_MEMORY" ] && echo "$DEVOPS_AGENT_MEMORY"
  ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  [ -n "$ROOT" ] && [ -d "$ROOT/.devops-agents/memory" ] && echo "$ROOT/.devops-agents/memory"
  [ -d "$HOME/.devops-agents/memory" ] && echo "$HOME/.devops-agents/memory"
}
```

Project entries win on conflict — they are more specific. When they conflict
in a way that changes behaviour, say so rather than silently preferring one.

No directory exists → memory is simply unavailable. Say so **once** if the
user asks you to remember something, offer to create it, and carry on. Never
treat a missing memory directory as an error.

## Layout

```
<memory-dir>/
  MEMORY.md            index — one line per entry
  instructions.md      standing instructions, freeform, always loaded
  entries/<slug>.md    one fact per file
```

## Entry format

```markdown
---
name: <kebab-case-slug>            # matches the filename
description: <one line a future session reads to judge relevance>
type: preference | convention | environment | incident | reference
scope: global | project
created: YYYY-MM-DD
---

<the fact, one or two sentences>

**Why:** <what makes it non-obvious — the failure it prevents>

**How to apply:** <what to do differently, concretely>
```

`**Why:**` is not decoration. An entry without it gets ignored or argued
with in three weeks.

Link related entries with `[[their-name]]`. A link to an entry that does not
exist yet is fine — it marks something worth writing.

## Index lines

```
- [Title](entries/<slug>.md) — <specific hook>
```

The hook decides whether a future session opens the file. Make it
discriminating:

```
✅  — chart repo bases on develop even though the remote advertises main
🚫  — base branch gotcha
```

## Writing rules

- **One fact per file.** So it can be corrected or deleted without touching
  anything else.
- **Update, do not duplicate.** Check the index for an entry that already
  covers it.
- **Absolute dates.** "Last Tuesday" is meaningless in a month.
- **Never store a secret.** A memory entry is not a credential store; record
  *where* a credential lives, never its value.
- **Never commit memory** to this toolkit's repo or quote it into a commit,
  PR, or public document.
