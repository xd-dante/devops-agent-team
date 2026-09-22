# Action — Review Comments

Address a review round: change, reply, then resolve.

## The order is not negotiable

```
make the change → reply saying what changed → resolve
```

A silently resolved thread tells the reviewer nothing and makes them re-check
the diff. Never resolve without a reply; never reply "done" without saying
what was done.

## Step 1 — Fetch every source

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
PR=$(gh pr view --json number --jq '.number')

gh api "repos/$REPO/pulls/$PR/comments" \
  --jq '.[] | {id, user: .user.login, path, line, body}'      # inline
gh api "repos/$REPO/pulls/$PR/reviews" \
  --jq '.[] | {id, user: .user.login, state, body}'           # summaries
gh api "repos/$REPO/issues/$PR/comments" \
  --jq '.[] | {id, user: .user.login, body}'                  # conversation
```

All three carry feedback. Inline comments alone are not the whole round.

## Step 2 — Triage

| Kind | Response |
|------|----------|
| Correct and actionable | Change it, reply with what changed |
| Correct but out of scope | Reply saying so; offer a follow-up ticket |
| Wrong | Reply with the evidence; leave **unresolved** until settled |
| Style point that does not apply here | Reply naming the rule that governs it |
| Automated reviewer | Same treatment as a human |

## Step 3 — Reply, then resolve

```bash
gh api "repos/$REPO/pulls/$PR/comments" \
  -f body="<what changed>" -F in_reply_to=<root-comment-id>

gh api graphql -f query='
  mutation($id: ID!) {
    resolveReviewThread(input: {threadId: $id}) { thread { isResolved } }
  }' -f id="<thread-id>"
```

Thread ids come from the GraphQL review-threads query; comment ids from the
REST calls above. Never resolve by guessing an id.

## Step 4 — Push and re-request

```bash
git push
gh pr view --json reviewDecision --jq '.reviewDecision'
```

After changes that alter the approach rather than polish it, re-request
review explicitly.

## Report

```
PR:        <url>
Comments:  <n> — addressed <a>, explained <b>, open <c>
Open:      <which, and what is unresolved>
Pushed:    <sha>     CI: <status>
Re-review: requested | not needed
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Resolving without replying | Reply first, always |
| "Done ✅" | Say what changed and why |
| Fetching only inline comments | Reviews and conversation too |
| Resolving a thread you disagree with | Leave it open with the evidence |
| Ignoring automated reviewers | Same treatment as a human |
| Assuming the reviewer saw the push | Re-request after substantive changes |
