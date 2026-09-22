---
name: aws-cost-analysis
description: 'Analyse and reduce cloud spend — break spend down by service and usage type, rightsize compute and databases, attack log-ingestion and observability cost, attribute data-transfer and NAT charges, and produce a ranked report with owners. Use when asked about cost, spend, the bill, savings, rightsizing, or commitment coverage. Strictly read-only; fixes route to infrastructure code.'
allowed-tools: Bash
---

# Cost Analysis

Find where the money goes, verify it against utilisation, and produce
recommendations that are ranked, owned, and honest about trade-offs.

**Strictly read-only.** Every fix lands as an infrastructure-code change.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Cost Breakdown | `actions/cost-breakdown.md` | Total → service → usage type → environment. Always first |
| Rightsize Compute | `actions/rightsize-compute.md` | Instances, nodes, databases, commitment utilisation |
| Observability and Transfer | `actions/observability-and-transfer.md` | Log ingestion, exporters, trails, flow logs, NAT and egress |
| Cost Report | `actions/cost-report.md` | Rank by saving per unit of effort; an owner per item |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Cost Principles | `standards/cost-principles.md` | The twelve rules that hold across accounts |
| Checklist | `standards/checklist.md` | Pre-report checks |

## Reference

Identity proof, profile resolution, read-only verbs and secret handling are
shared with `../aws-investigate/standards/` and apply here unchanged.

## Principles

1. **Measure before optimising.**
2. **Drill to usage type** — a service total is not a finding.
3. **Ingestion dwarfs storage** — cut emission, not retention.
4. **Attribute, do not assume** — egress volume is often CI, not the app.
5. **Rank by saving per unit of effort.**
6. **Every item has an owner.**
7. **Trade-offs go inside the recommendation.**
8. **Never present an estimate as a measurement.**

## Usage

1. Load this manifest, `standards/cost-principles.md`, and
   `../aws-investigate/standards/read-only-rules.md`.
2. Prove the identity and fix the period.
3. Run `actions/cost-breakdown.md`, then the categories it points at.
4. Produce `actions/cost-report.md`; validate against
   `standards/checklist.md`.
