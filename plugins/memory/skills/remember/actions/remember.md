# Action — Remember

Write a fact to memory. Triggered when the user says so: *"keep in mind"*,
*"remember this"*, *"save this"*, *"note that"*, *"don't do that again"*,
*"from now on"*, *"always"*, *"never"*.

## Step 1 — Decide whether it qualifies

Check against `standards/what-to-remember.md`.

Already in the code, in git history, or in this toolkit's own rules → **say
so and do not store it.** Ask what was non-obvious about it and store that
instead. An index full of things the code already says is worse than an empty
one: it goes stale and then misleads.

## Step 2 — Pick the scope

| Scope | When |
|-------|------|
| `project` | True of this codebase only — branch layouts, which repo owns what |
| `global` | True of how the user works everywhere — preferences, standing rules |

Unsure → project. A wrongly-global entry misfires in every other repo.

Project scope needs a project directory. Creating one means also adding
`.devops-agents/` to that repo's `.gitignore` **in the same step** — it sits
inside their repository and can be committed by accident. Cannot write that
`.gitignore` → use global scope and say why.

## Step 3 — Check for an existing entry

```bash
grep -ril "<key terms>" "$d/entries/" 2>/dev/null
grep -i "<key terms>" "$d/MEMORY.md" 2>/dev/null
```

Found → **update it.** Two entries on one fact drift apart and then
contradict each other.

## Step 4 — Write it

```bash
cat > "$d/entries/<slug>.md" <<'ENTRY'
---
name: <slug>
description: <one line a future session reads to judge relevance>
type: preference | convention | environment | incident | reference
scope: global | project
created: <YYYY-MM-DD>
---

<the fact, one or two sentences>

**Why:** <what makes it non-obvious — the failure it prevents, or the
correction that produced it>

**How to apply:** <what to do differently, concretely>
ENTRY
```

`**Why:**` is mandatory. Without it the entry gets ignored or argued with
later — the reasoning is what makes a rule survive.

Absolute dates. Never a secret value — record where a credential lives, not
what it is.

## Step 5 — Index it

Append to `MEMORY.md`:

```
- [Title](entries/<slug>.md) — <discriminating hook>
```

The hook decides whether a future session opens the file:

```
✅  — chart repo bases on develop even though the remote advertises main
🚫  — base branch gotcha
```

## Step 6 — Confirm, briefly

```
Saved to memory (<scope>): <slug> — <one line>
```

One line. The user asked for a note, not a ceremony.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Storing what the code already says | Ask what was non-obvious; store that |
| A second entry for a covered fact | Update the existing one |
| Global scope by default | Project when unsure |
| Omitting `**Why:**` | It is what makes the entry survive |
| Relative dates | Absolute, always |
| Storing a credential value | Store its location |
| Creating a project directory without gitignoring it | Same step, or use global |
| A vague index hook | Make it discriminating |
