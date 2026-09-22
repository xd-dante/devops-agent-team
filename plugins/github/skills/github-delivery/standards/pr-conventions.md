# PR Conventions

## Title

`<type>: [<TICKET>] <2–5 words>` — configurable via `vcs.pr_title_template`.

No leading verb, ~50 character ceiling. Same rule as ticket titles: the type
carries the verb.

```
✅  feat: [PROJ-412] Runner image pin
✅  fix: [PROJ-418] Probe timeout
🚫  feat: [PROJ-412] Add a pin to the runner image so CI stops breaking
```

## Body

- What changed and why, briefly
- **Apply or merge order** across repos, when one exists
- Live-verification notes where something was checked against a real
  environment
- Footer linking the ticket

Rationale that does not belong in a code comment belongs here. This is where
the reasoning for a change lives — not in the files.

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
