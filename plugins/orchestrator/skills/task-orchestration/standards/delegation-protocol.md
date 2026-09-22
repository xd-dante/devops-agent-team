# Delegation Protocol

## 1. Classify first

One line each, for yourself:

- **Goal** — what "done" looks like in the user's words
- **Domain(s)** — resolved via `routing-table.md`
- **Mutation?** — does this change infrastructure, a cluster, or a repo
- **Environment** — unstated is *not* production, and *not* safe either. Ask

**🛑 STOP and ask** when the domain is still ambiguous after the
disambiguation rules, when a mutating task has no stated environment, or when
a protected environment is the target without the user saying so.

## 2. Brief self-contained

A specialist starts with **no conversation history**. Every brief carries:

| Field | Why |
|-------|-----|
| Objective | One sentence, outcome-shaped |
| Scope boundary | What it must not touch |
| Environment + cloud profile | Wrong-account work is the top failure mode |
| Absolute paths | Repo root, worktree path, file paths |
| Ticket id | So it can pull its own context |
| Established facts | Stops it re-deriving what this session knows |
| Required output | Findings? A diff? A PR link? Name it |

"See above" and "as discussed" are meaningless to a cold agent.

## 3. Parallel vs sequential

- **Parallel** — disjoint reads, neither needs the other's output.
- **Sequential** — one's output is the other's input, or an apply order
  exists.
- **Never** two mutating agents at the same target at once.

## 4. Verify

A report is evidence, not a verdict:

- Does the stated evidence support the conclusion?
- Did the agent stay in its boundaries — did a read-only agent mutate?
- Spot-check one path, id, or number against the real source.
- Two specialists disagreeing → name the conflict and the cheapest settling
  check. Never average them into a soft answer.

Re-dispatch with a sharper brief rather than quietly doing the specialist's
job and presenting it as theirs.

## 5. Escalate rather than improvise

Return to the user when the work needs a mutation the owning agent is
forbidden to make, when a protected environment is involved and unconfirmed,
when a required plugin is disabled, or when findings conflict on a fact that
changes the fix.

## 6. Report once

One consolidated report per task, per `report-format.md`. No per-agent
transcript dumps — the user asked you, not the team.
