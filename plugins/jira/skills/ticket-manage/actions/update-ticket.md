# Action — Update Ticket

Record an outcome and move the status.

## Step 1 — Comment before transitioning

A status change with no explanation is a dead end for the next reader.
Conclusion first, then evidence, then links.

✅ Good:

```
Not introducing a connection proxy. Minimum cost exceeds the instance it
would front, and it multiplexes rather than raising the connection ceiling —
pinning behaviour (session-level statements, advisory locks, temp tables)
degrades it further.

Recommendation: move up one instance class where the ceiling is hit, which
roughly doubles available connections. Revisit the proxy only if connection
churn during deploys becomes the actual problem.
```

🚫 Useless — no conclusion, no evidence, no decision:

```
Looked into this, seems complicated. Will think about it more.
```

## Step 2 — "Not doing this" needs its reasoning

Closing as rejected is a legitimate outcome and the reasoning **is** the
deliverable. Never transition to a resolved state on "decided against it".

## Step 3 — Read the available transitions

Workflows differ by issue type and project. Fetch the available transitions
and pick from them. If the intended status is not offered, stop and report —
the workflow does not permit that move from the current state.

## Step 4 — Field updates

| Field | When |
|-------|------|
| Pull request / links | When a PR opens — with a comment carrying the URL |
| Acceptance criteria | When scope is refined, with a comment saying why |
| Estimate | On estimation |
| Parent | To attach to a hierarchy |

Every field change that alters meaning gets a comment. Silent scope edits are
worse than no edit.

## Report

```
Ticket:     <KEY> — <tracker-url>/browse/<KEY>
Comment:    added — <one-line summary>
Transition: <from> → <to>   (or: not transitioned, and why)
Fields:     <what changed>
PRs linked: <urls>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Transitioning without a comment | Comment first, always |
| Guessing a transition name | Read the available transitions |
| Closing as rejected with no reasoning | The reasoning is the deliverable |
| Silent scope edits | Every meaning-changing edit gets a comment |
| A running log of micro-updates | One comment per meaningful outcome |
| Transitioning someone else's ticket unprompted | Ask first |
