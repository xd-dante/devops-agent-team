# Action — Findings Report

The entry point for a full security-posture review. Runs the three focused
actions in order and writes one report a reviewer can act on without the
transcript.

## Step 1 — Scope

State before reading anything:

- every account in scope and the profile used for each
  (`aws sts get-caller-identity` per profile)
- the regions to probe, normally every enabled region
- whether a production account is in scope; if its session is unavailable,
  say so and carry on with what the administrator account can see

## Step 2 — Run the actions in order

| Order | Action | Produces |
|-------|--------|----------|
| 1 | `actions/findings-inventory.md` | topology, `findings.json`, `findings.tsv`, `active-ids.txt` |
| 2 | `actions/opsitem-backlog.md` | generator, `ops.tsv`, `stale.tsv`, `live-backed.tsv` |
| 3 | `actions/fix-plan.md` | fix table, suppress list, triage list |

Each later step reads the files the earlier one wrote. Keep everything in one
working directory per run and note when the pull happened: staleness is only
true as of that pull.

## Step 3 — Write the report

Use `standards/report-format.md`. Write it to
`security-findings-<date>.md` in the working directory, then summarise the
headline, the top five quick wins and the open questions in chat.

## Step 4 — Hand off

| Finding | Hand to |
|---------|---------|
| A fix in infrastructure code | `terraform-engineer`, via the orchestrator |
| A bulk resolve of stale items | orchestrator. It is a mutation; the user approves the prepared list |
| A runtime-threat finding needing pod or cluster evidence | `kubernetes-investigator` (read-only, direct) |
| A cost concern raised by enabling a control | `aws-cost-analyzer` |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Starting with `get-findings` | Establish topology first. The count depends on it |
| Writing the report only in chat | Write the file. Reviewers need to act on it later |
| Mixing pull times across steps | One working directory and one pull time per run |
| Recommending a bulk resolve without the list | Ship `stale.tsv` with its row count and how it was built |
| Omitting what was not checked | Section 9 of the report is mandatory |
