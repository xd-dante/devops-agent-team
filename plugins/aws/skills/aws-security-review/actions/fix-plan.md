# Action — Fix Plan

Turn the live critical and high findings into a ranked list of changes. Each
change has resources, an owner, an effort and a risk.

## Step 1 — Select

From `findings.tsv`, take critical and high first. Pull full payloads for
those ids only (batch by about 20):

```bash
aws securityhub get-findings --filters '{"Id":[{"Value":"<id1>","Comparison":"EQUALS"}, …]}' \
  --query 'Findings[].{id:Id,acct:AwsAccountId,ctl:Compliance.SecurityControlId,why:Compliance.StatusReasons,res:Resources[].Id,detail:ProductFields}'
```

## Step 2 — Group by fix, not by finding

One change often clears many findings: the same group, the same image, the
same account setting. For each group, establish:

| Field | How |
|-------|-----|
| Resources | ids from the payload, verified live with a describe call |
| Why it fails | `Compliance.StatusReasons`, or the product's detail section, quoted |
| Owning code | grep **every** infrastructure repo on its base branch (`git show origin/<base>:<path>`), not a worktree |
| Drift | code is compliant but live is not, so a manual change or an unapplied merge |
| Effort / risk | S/M/L, and what breaks if the change is wrong |
| Confirmation | who must agree first (a resource marked temporary, a shared dependency) |

## Step 3 — Recognise the recurring causes

| Pattern | What to check | Typical owner |
|---------|---------------|---------------|
| Manual rules on a code-managed group | module manages rules as separate resources, so apply never reverts them | manual removal, then keep code as is |
| Orphans from a deleted cluster or service | zero attachments, zero references | manual removal with the pre-check |
| Committed build artefact (zipped function) | manifest bumped, artefact not rebuilt | rebuild + targeted apply; CI follow-up |
| Image filter fixed in code, hosts unchanged | instance launch date vs code change | apply + instance refresh |
| Health-check or status port exposed publicly | is a load balancer health-checking that port? | chart or module values; design check first |
| Account-level control off | not declared anywhere in code | add to the account baseline module |
| Control enabled in code but failing live | drift, or a stale evaluation | re-check after the next evaluation |

Before recommending a port or rule removal, check what depends on it: target
group health checks, listeners and peering sources. A finding fix that takes
down a health check is an outage.

## Step 4 — Suppress instead, when it is by design

Say why, for example "public ingress on 443 by design", "informational
notice" or "not applicable in non-production". Never suppress a vulnerability
or runtime-threat finding to make the number smaller.

## Step 5 — Runtime-threat findings

These are not quick wins. For each group, give:

- the process, the direction (local and remote addresses) and the time
- the most likely benign explanation, **labelled as a hypothesis**
- the confirming check: audit log, session log, pod spec, image contents
- what to do if the check cannot be run, for example "treat as an incident"
  when logs are past retention and nobody can explain the activity

Route pod and cluster evidence to `kubernetes-investigator`.

## Report (feeds sections 5–7 of the full report)

```
| # | Fix | Clears (n, severity, accounts) | Resources | Owner (repo:file | manual) | Effort | Risk | Prerequisite |
Suppress: | item | reason |
Triage:   | finding | evidence | hypothesis | confirming check |
After each fix: resolve the matching operations items (both copies where mirrored).
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| One row per finding | Group by the change that clears them |
| "Unmanaged" after one repo grep | Check every infrastructure repo on its base branch |
| Removing a port without checking its consumers | Look at health checks and listeners first |
| Calling a reverse-shell finding benign by pattern | Give the confirming check and keep it open |
| Forgetting the resolve step after the fix | Items do not close themselves |
