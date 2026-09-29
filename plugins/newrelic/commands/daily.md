---
description: Daily observability check — report only what needs attention, and who owns it
argument-hint: "[hours] (default 1)"
---

# Daily observability check

One scripted sweep, then judgement. The script transports the data so the
context does not: four batched queries in one process, a digest of roughly ten
lines out. Do **not** re-issue these queries as individual tool calls.

## Step 1 — Resolve configuration

From `.devops-agents.yml` (walk up from cwd), `observability:`:

| Key | Use |
|-----|-----|
| `region` | `US` or `EU` — a wrong region returns an **empty account, not an error** |
| `accounts` | alias → account id. An alias starting `prod` is weighted as production |
| `suppress` | alert-condition names that are known noise |
| `thresholds.error_rate_pct`, `thresholds.p95_latency_ms` | regression gates |

Key from `$NEW_RELIC_API_KEY`. If it is unset, stop and say so — do not fall
back to the MCP server for a daily run: its OAuth access token is short-lived
and needs a browser round-trip when refresh fails, which defeats an unattended
check.

## Step 2 — Run it

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/nr-daily.py" \
  --region "$REGION" \
  --account prod=<id> --account nonprod=<id> \
  --hours "${1:-1}" \
  --suppress '<condition name>'
```

Exit `2` means a check could not run. Then the verdict is **could not
verify** — never "all clear".

## Step 3 — Route, don't just relay

The script grades severity; you add ownership. Every 🔴 and 🟠 names the agent
that takes the next step, or it is an observation rather than a hand-off:

| Finding | Owner |
|---------|-------|
| node memory / pod not ready / capacity | `kubernetes-investigator` |
| throughput collapse, error-rate jump on a service | `kubernetes-investigator`, then the deploy |
| entity not reporting | whoever owns that service's delivery — the agent is silent, not the service necessarily down |
| managed database, network path, IAM denial | `aws-investigator` |
| a condition marked **chronic** | not an incident — a threshold to fix, route to whoever owns the alert policy |

Read `standards/signal-triage.md` before grading anything the script left
ungraded.

## Step 4 — Report

Print the digest as-is, then add at most three lines of judgement: what
changed since yesterday, what is chronic and should be fixed rather than
watched, and the single thing worth doing first.

A chronic finding repeated every morning is a failure of the check, not a
finding. Say so and propose the threshold change.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Re-running the queries as separate tool calls | The script exists to keep them out of context |
| "All clear" when exit code was 2 | A failed check means could not verify |
| Relaying chronic noise every day | Name it chronic, propose the threshold fix |
| Treating non-prod CRITICAL as act-now | Production weighting is deliberate |
| Findings with no owner | Name the agent that takes the next step |
