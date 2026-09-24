# Delivery Checklist

## Before branching
- [ ] Base branch **probed**, not taken from the advertised default
- [ ] Base fetched fresh
- [ ] New branch — not one whose PR already merged
- [ ] Branch name describes the actual change

## Before committing
- [ ] Staged diff reviewed
- [ ] Conventional format, scopeless unless configured otherwise
- [ ] No `-s` / `--signoff`
- [ ] No AI or assistant attribution anywhere
- [ ] No secrets, state files, `.env` or kubeconfig
- [ ] Unrelated formatting churn reverted
- [ ] Deletions audited with a **three-dot** diff (`origin/$BASE...HEAD`) —
      every `-` line accounted for
- [ ] Submodule pointer **excluded** from the parent commit

## Submodules
- [ ] Initialised before being written against
- [ ] Its base pulled, not just checked out
- [ ] Own branch, own PR, own base
- [ ] Submodule PR URLs reported with the parent's

## PR
- [ ] Targets the probed base
- [ ] Title `<type>: [<TICKET>] <2–5 words>`, no leading verb
- [ ] Body states what, why, and any apply or merge order
- [ ] Ticket linked
- [ ] CI checked after push

## Review
- [ ] Every comment has a reply saying what changed
- [ ] Replies posted **before** resolving
- [ ] Nothing resolved silently
- [ ] Disagreements evidenced and left open until settled
- [ ] Review re-requested after substantive changes

## Reporting
- [ ] Every PR URL inline, plus an end-of-reply recap
- [ ] Merge order stated where one exists
- [ ] Anything unfinished stated explicitly
