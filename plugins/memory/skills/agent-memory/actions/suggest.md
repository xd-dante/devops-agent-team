# Action — Suggest

Self-learning. Notice when something is worth remembering, and **offer** to
save it. This is the action that makes memory accumulate without the user
having to think about it.

## The rule

**Offer. Never save silently.**

Memory shapes future behaviour, so the user decides what goes in. An agent
that writes its own rules unprompted becomes unpredictable, and the user
loses the ability to reason about why it did something.

## Triggers

| Signal | Why it is worth capturing |
|--------|---------------------------|
| The user corrects how you worked | A preference stated once is a preference |
| The user corrects the **same thing again** | Strongest signal there is. Offer immediately, and say it is the second time |
| You spent real effort rediscovering a site fact | The next session pays it again otherwise |
| A decision was made with reasoning, including a "no" | Stops it being re-proposed in a month |
| You hit a failure with a **silent** signature | Silent failures are the expensive ones |
| The user says "actually", "no, we", "we don't", "we always" | Organisational convention leaking out |
| The same question comes up twice in a session | Either memory is missing, or an index hook is too vague |

## Not triggers

- Task state or progress
- Anything the code, git history, or this toolkit's rules already say
- A one-off answer with no future bearing
- Your own reasoning that turned out fine

## Step 1 — Draft it

Same shape as `actions/remember.md`: fact, `**Why:**`, `**How to apply:**`,
scope. Draft it properly before offering — "shall I remember something about
branches?" is not a proposal.

## Step 2 — Offer, with the text visible

```
Worth remembering? You have corrected this twice now.

  scope: project
  type:  convention
  ---
  Open PRs against `develop` in this repo, never `main`.

  **Why:** the remote advertises `main` as the default, so anything deriving
  the base automatically picks the wrong branch.

  **How to apply:** pass the base explicitly on the create call; probe
  `origin/develop` rather than trusting the advertised default.

Save it? (or tell me what to change)
```

Showing the text matters: the user is approving specific wording that will
steer future work, not a vague intent.

## Step 3 — On yes

Run `actions/remember.md` from step 3 onward — duplicate check, write, index,
one-line confirmation.

## Step 4 — On no

Drop it and **do not offer that fact again this session.** A second offer
after a decline is nagging, and it trains the user to ignore the prompts
that matter.

## Timing

- At a natural pause — after a step completes, not mid-command
- **Batch** at the end of a task when several things accrued
- At most **two or three** offers per task. Past that you are interrupting
  rather than learning
- Never between a plan and its approval, or anywhere it would sit between
  the user and a decision they are making

## Report

Nothing separate. The offer is the output.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Saving without asking | Always offer |
| Offering without showing the text | The wording is what gets approved |
| Offering the same fact after a decline | Once per session, then drop it |
| Interrupting mid-task | Wait for a pause; batch at the end |
| Offering on every small thing | Two or three per task, maximum |
| Proposing something the code already says | Not a trigger |
| Missing a repeated correction | The strongest signal — say it is the second time |
