---
name: aws-security-review
description: 'Review the cloud security posture backlog — inventory open Security Hub findings and their OpsCenter operations-item mirrors, find what generates them, separate stale items from live ones, rank live findings by fix with owners, and write one reviewable report. Use when asked about security findings, Security Hub, GuardDuty or Inspector results, a large or growing OpsCenter backlog, or "what can we fix quickly". Strictly read-only; resolves, suppressions and fixes route through the orchestrator.'
allowed-tools: Bash
---

# Security Findings Review

Turn a security-posture backlog into a short list of decisions: what is
noise, what is stale, what one change would clear, and what genuinely needs
a human to look at it.

**Strictly read-only.** Resolving items, changing finding workflow,
suppressing, disabling controls and changing integration settings are all
mutations. This skill produces the evidence and the exact lists; the
orchestrator routes the change and a human approves it.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Full Review | `actions/findings-report.md` | Entry point: runs the three below in order, then writes the report |
| Findings Inventory | `actions/findings-inventory.md` | Topology, enabled standards, finding counts, noise generators |
| Operations Backlog | `actions/opsitem-backlog.md` | What creates the items, stale vs live join, prepared resolve lists |
| Fix Plan | `actions/fix-plan.md` | Group live findings by fix, owner, effort, risk, suppress-instead |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Read-Only Rules | `standards/read-only-rules.md` | Allowed verbs, and the security-service verbs that look harmless but mutate |
| Finding Sources | `standards/finding-sources.md` | How findings and items are generated and why they never close themselves |
| Report Format | `standards/report-format.md` | The reviewable report shape |
| Checklist | `standards/checklist.md` | Pre-report checks |

## Principles

1. **Topology before counts.** An administrator account sees every member's
   findings, so a total means nothing until you split it by account.
2. **Find the generator, not just the count.** One setting or one ephemeral
   workload usually explains most of the volume.
3. **Open is not live.** Operations items never close when their finding
   resolves, so join them to the active findings before calling anything a
   problem.
4. **Rank by fix, not by finding.** One change often clears dozens.
5. **Runtime-threat findings are never quick wins.** Give the confirming
   check; do not call one benign by pattern.
6. **Read-only; the fix goes to code.** Name the owning repo and agent, or
   mark it "manual" with the pre-check that proves it is safe.

## Usage

1. Load this manifest and `standards/read-only-rules.md`.
2. Prove the identity and list the regions in scope.
3. Execute `actions/findings-report.md`, or a single capability.
4. Validate against `standards/checklist.md`.
