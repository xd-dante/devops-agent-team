# Agent Memory Discipline

Each agent declares `memory: user`, giving it
`~/.claude/agent-memory/<agent-name>/`. The harness injects the first
**200 lines or 25KB** of that directory's `MEMORY.md` into the agent's system
prompt, and enables Read/Write/Edit so the agent curates it.

That is accrued craft: what this specialist learned about this estate. It is
powerful and it is unsupervised — nobody approves a write. These rules exist
because a wrong line in `MEMORY.md` is read as fact at the start of every
future task.

## Three tiers, and who writes which

| Tier | Lives in | Written by | Scope |
|------|----------|-----------|-------|
| Standing instructions | `instructions.md` in the memory directory | the user, via `actions/remember.md` | every agent, outranks agent defaults |
| Shared estate facts | `entries/<slug>.md` | offered by an agent, **approved by the user** | every agent |
| Accrued craft | `~/.claude/agent-memory/<agent>/MEMORY.md` | the agent, automatically | that one agent |

Read all three before planning. Write to the third freely, to the second only
by offering, and to the first never.

## The 200-line limit is a budget, not a truncation to work around

Past the limit the rest is not read. So `MEMORY.md` is a curated page, never a
log:

- **Supersede, do not append.** A corrected fact replaces the old line.
  Two lines that disagree make both useless.
- **Date what decays.** `2026-10-01: prod runners are on the micro pool`
  invites a re-check; the same line undated hardens into folklore.
- **One line per fact** where a line will do. Prose belongs in an entry file
  under the shared tier.
- When the file approaches the limit, **delete the least load-bearing line**
  rather than letting the tail fall off silently.

## What qualifies

All four, not three:

1. **Durable** — true next week, not just for this task.
2. **Non-obvious** — not derivable from the repo, the git history, or a
   `--help`.
3. **Expensive to rediscover** — it cost a wrong turn to learn.
4. **Yours** — about your domain. A Terraform fact in the Kubernetes agent's
   memory is noise in one place and missing in another.

Good: *"`terraform workspace select` on a missing workspace silently no-ops —
check `workspace show` after selecting."*

Bad: *"The RDS module is at modules/rds."* — the repo says that.

## What never goes in

- **Task state.** What you are doing now, a ticket id, a PR number. Memory is
  not a scratchpad; the conversation is.
- **Anything the repo already records.** Structure, module paths, past fixes,
  commit history, `CLAUDE.md` content.
- **Secrets.** Keys, tokens, passwords, connection strings — in any form,
  including "the key starts with". A memory file is plaintext and is read into
  a prompt on every task.
- **An unverified assumption.** The most damaging category, because it reads
  identically to a verified one.

## Record how you know

Every line carries its evidence, in the line:

```
2026-10-01: helm-charts base branch is develop, not main — verified with
`git remote show origin` and `gh repo view --json defaultBranchRef`; the repo
map document says main and is wrong.
```

"Verified with X" is what lets a future reader trust or re-check it. A line
that cannot say how it was learned is an assumption, and does not go in.

**Observed, not inferred.** That a command exists is not evidence it works;
that a document claims something is not evidence it is true. If a reviewer,
a document and the system disagree, the system wins and the line says so.

## Promote what others need

Your memory is private to you. An estate-wide fact kept there means eleven
other agents will each rediscover it, and may disagree about it.

When a fact matters beyond your domain, **offer it for the shared tier** via
`actions/suggest.md` — which offers and never saves silently. Keep a short
pointer in your own `MEMORY.md` if you like, but the shared entry is then the
source of truth, and a divergence between the two is a bug you fix.

Signals a fact is estate-wide rather than yours: it names a repository, a
branch convention, an environment, an account, a cluster, or a person's
preference.

## When memory contradicts reality

The system is right. Correct the line immediately — do not work around it, and
do not leave both versions. If the stale line came from the shared tier,
report it rather than silently diverging from it.

An entry describes what was true when written. Before acting on one, confirm
anything it asserts about a file, a flag, or a resource still exists.

## It never leaves the machine

Not into a commit, a pull request, a ticket, a public document, or this
repository. The directory holds exactly the site-specific material this
toolkit must never contain.

A *lesson* may be generalised into a rule and contributed upstream. The fact
stays local. "Pin the chart version before promoting" is a rule; "promote
whitebox-uat first" is a fact.
