# PR Conventions

## Title

`<type>: [<TICKET>] <2–5 words>` — configurable via `vcs.pr_title_template`.

No leading verb, ~50 character ceiling, **no trailing period**. Same rule as
ticket titles: the type carries the verb.

```
✅  feat: [PROJ-412] Runner image pin
✅  fix: [PROJ-418] Probe timeout
🚫  feat: [PROJ-412] Add a pin to the runner image so CI stops breaking
```

## Body

Fixed template — fill every section, omit `Test plan` only if there is
genuinely nothing to check:

```markdown
## What
<Feature/behavior-level description: components introduced, integrations,
scope boundaries, what's intentionally out of scope. Reviewers read this
first.>

## Why
<Motivation. Reference the spec/ticket/incident. The problem this solves and
the constraint that shaped the approach.>

## How
<Architectural/behavioral summary only. 2–5 short bullets: key design
decisions, non-obvious trade-offs, apply/merge order across repos when one
exists. Not a per-file inventory — the diff shows that.>

## Test plan
- [ ] <what to verify>
- [ ] <edge case to check>

Ticket: <ticket url>
```

Rationale that does not belong in a code comment belongs here — not in the
files. Omit the whole `Ticket:` line for changes with no ticket in scope.
Exactly one ticket per PR: one link in the title, one `Ticket:` line in the
body.

### No manual line-wrapping

Write every paragraph as **one unbroken source line**, however long. Do not
wrap prose at a fixed column (~70–80 chars) the way a terminal or editor
would — GitHub renders a bare `\n` inside a paragraph as a hard line break,
not a soft wrap, so manually-wrapped prose renders as a jagged, uneven right
margin instead of a normal flowing paragraph. A blank line is the only
paragraph break; inside a paragraph, no newline at all.

This bites most often when the body is composed inside a bash heredoc —
generating the text with a self-imposed wrap column produces literal `\n`
bytes in the file. Compose each paragraph as a single line before it goes
into the heredoc, and write the body to a temp file for `--body-file`
instead of an inline `--body "$(cat <<'EOF' ... )"` if that makes it easier
to avoid accidental wrapping.

Exactly one blank line between sections and list items — never two. Do not
leave a trailing blank line before the closing `Ticket:` line or at the end
of the file.

## Target

The probed base branch. Confirm it explicitly on the create call rather than
relying on the remote's default.

## Merge

| Scenario | Method |
|----------|--------|
| Feature → integration branch | Squash and merge |
| Release → production branch | Merge commit (`--no-ff`) |
| Hotfix → production branch | Merge commit (`--no-ff`) |

Delete the branch after merge, local and remote. Never merge your own PR
without at least one approval, unless the team has explicitly agreed
otherwise.

## Submodules

A changed submodule ships on its **own** branch and its **own** PR against
its own base. The parent commit **excludes** the submodule pointer — the pin
stays on base until the submodule PR merges, then moves as a deliberate
follow-up.

Never push a pointer bump directly to a protected branch.

## Links

Every PR gets its URL inline on first mention. End the reply with a recap of
every PR opened or updated. A PR the reader has to go and find is a PR they
will not read.
