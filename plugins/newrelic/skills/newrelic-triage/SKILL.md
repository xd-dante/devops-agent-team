---
name: newrelic-triage
description: 'Check observability state and report what needs attention — a fast daily digest of open issues, entity health and dashboard breakage; a periodic audit of whether the alerting would actually fire; golden signals for one service; and ad-hoc NRQL for a specific question. Use when asked whether anything is wrong, for a daily or morning check, why a service is slow or erroring, whether alert coverage has gaps, or to run a specific metrics query. Strictly read-only.'
allowed-tools: Bash
---

# Observability Triage

Answers **"is anything actually wrong, and does it need me?"** in a few
lines — then goes deeper only where asked.

Built for someone who does not have time to open the UI every day: verdict
first, exceptions only, known noise suppressed and counted.

**Strictly read-only.** A daily check is only worth running if it is
trustworthy, and an agent that can also silence alerts cannot be trusted to
report them.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Daily Digest | `actions/daily-digest.md` | The default run: issues, entity health, golden signals, dashboard spot-check, recent deploys → one verdict |
| Alert Review | `actions/alert-review.md` | Periodic audit: disabled conditions, conditions that can never fire, uncovered services, policies that notify nobody |
| Entity Health | `actions/entity-health.md` | Golden signals for one service, with the deploy timeline |
| Dashboard Review | `actions/dashboard-review.md` | Broken and misleading widgets; coverage gaps |
| NRQL Query | `actions/nrql-query.md` | A specific question, asked directly |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Account Discovery | `standards/account-discovery.md` | Region and account resolution, verified query shapes, the MCP-optional rule |
| Read-Only Rules | `standards/read-only-rules.md` | Forbidden mutations, data handling, query cost |
| Signal Triage | `standards/signal-triage.md` | Severity ladder, default thresholds, comparison rule, what "all clear" may mean |
| Checklist | `standards/checklist.md` | Per-run checks |

## Principles

1. **Verdict first, exceptions only** — three lines is the success case, not
   a lazy one.
2. **"All clear" requires every check to have run.** A failed query makes the
   verdict *could not verify*, never all clear.
3. **A number needs its baseline** — compare the same hour week over week;
   daily shape dominates most traffic.
4. **Suppress noise, but count it** — an unread report is a useless one.
5. **A silent entity is a failure** — `reporting = false` raises no alerts and
   looks healthy.
6. **The wrong region returns an empty account**, not an error. Prove the
   account first.
7. **Every finding names an owner** — a finding with no route is an
   observation.
8. **Read-only.** Acking and muting are mutations with real consequences for
   other people.

## Usage

1. Load this manifest and `standards/account-discovery.md`; prove the account.
2. Default to `actions/daily-digest.md` unless a specific question was asked.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md` before reporting.
