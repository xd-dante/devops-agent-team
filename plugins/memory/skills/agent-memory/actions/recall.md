# Action — Recall

Load what is already known, at the start of a task. Cheap, and it is what
stops an agent re-deriving a fact the user explained last week.

## Step 1 — Resolve the directories

```bash
DIRS=$(
  [ -n "$DEVOPS_AGENT_MEMORY" ] && echo "$DEVOPS_AGENT_MEMORY"
  ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
  [ -n "$ROOT" ] && [ -d "$ROOT/.devops-agents/memory" ] && echo "$ROOT/.devops-agents/memory"
  [ -d "$HOME/.devops-agents/memory" ] && echo "$HOME/.devops-agents/memory"
)
```

None exist → memory is unavailable. Continue without it; do not treat it as
an error and do not mention it again unless the user asks you to remember
something.

## Step 2 — Load the cheap files in full

```bash
for d in $DIRS; do
  cat "$d/instructions.md" 2>/dev/null
  cat "$d/MEMORY.md" 2>/dev/null
done
```

`instructions.md` is **user instruction** — it outranks your own defaults and
the toolkit's. `MEMORY.md` is an index of hooks, not content.

## Step 3 — Open only what looks relevant

Read the index hooks, pick the entries that bear on this task, open those.
Opening everything defeats the point of an index.

```bash
cat "$d/entries/<slug>.md"
```

Two or three entries is normal. Ten means the index hooks are too vague —
worth mentioning to the user.

## Step 4 — Verify before acting

An entry records what was true when written. If it names a file, function,
branch, flag, or resource, **check it still exists** before relying on it.

Reality disagrees with an entry → reality wins, and the entry is now wrong.
Say so and offer `actions/forget.md`. Silently working around a wrong entry
leaves it to mislead the next session.

## Step 5 — Handle conflicts

Project and global entries disagreeing is normal — project is more specific
and wins. But if the disagreement changes what you would do, **say so** and
name which you followed.

## Report

Only when memory actually changed your approach:

```
Memory: applied <n> entries — <slug>, <slug>
        <the one that mattered, and how it changed the approach>
```

Silence otherwise. Narrating every recall is noise.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Loading every entry | Open only what the hooks suggest |
| Treating a missing directory as an error | Memory is optional |
| Treating `instructions.md` as advisory | It is user instruction; it outranks defaults |
| Acting on a stale entry | Verify anything it names still exists |
| Silently preferring one side of a conflict | Say which you followed |
| Announcing recall on every task | Report only when it changed something |
