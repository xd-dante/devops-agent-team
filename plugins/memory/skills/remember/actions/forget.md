# Action — Forget

Correct or delete an entry. A wrong memory is worse than no memory: it is
confidently misleading, and it survives until somebody deals with it.

## Triggers

- The user says to forget, drop, or ignore something
- An entry contradicts reality — the branch, file, flag, or resource it names
  no longer exists or behaves differently
- The user contradicts an entry in passing ("no, we moved off that")
- Two entries disagree with each other

## Step 1 — Find it

```bash
grep -ril "<terms>" "$d/entries/" 2>/dev/null
grep -in "<terms>" "$d/MEMORY.md" 2>/dev/null
```

Check both scopes. The stale entry is often the global one, because project
facts get corrected more often.

## Step 2 — Correct, or delete

| Situation | Do |
|-----------|----|
| The fact changed | **Update** the entry and its index hook. Keep the slug — inbound `[[links]]` still resolve |
| The fact was never right | **Delete** the entry and its index line |
| Superseded by a broader entry | Delete the narrow one; link it from the broader one |
| Two entries disagree | Establish which is true, fix that one, delete the other |

Prefer correcting over deleting where the subject still matters. A corrected
entry keeps the reasoning; a deletion loses it.

## Step 3 — Delete cleanly

```bash
rm "$d/entries/<slug>.md"
# remove its line from MEMORY.md
```

Never leave an index line pointing at a missing file, and never leave an
orphan file out of the index — an unindexed entry is invisible.

## Step 4 — Check inbound links

```bash
grep -rl "\[\[<slug>\]\]" "$d/entries/" 2>/dev/null
```

Update anything that referenced a deleted entry. A dangling link is
tolerable; a dangling link plus a contradictory claim is not.

## Step 5 — Say what changed

```
Memory updated (<scope>): <slug> — <corrected: what changed | deleted: why>
```

## Never

- Delete an entry the user did not ask about, on your own judgement, unless
  it is demonstrably false — and then say so
- Delete when correcting would keep useful reasoning
- Edit an entry to match what you wish it said

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Working around a wrong entry silently | Correct it; otherwise it misleads the next session |
| Checking one scope only | The stale one is often global |
| Deleting when the subject still matters | Correct it and keep the reasoning |
| Leaving a dangling index line | Remove both file and line |
| Changing the slug on a correction | Keep it; inbound links resolve |
| Pruning entries unprompted | Ask, unless demonstrably false |
