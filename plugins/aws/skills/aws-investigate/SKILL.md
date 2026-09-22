---
name: aws-investigate
description: 'Investigate cloud resource behaviour — locate a resource and its owning code, diagnose managed-database connection and performance problems, trace a failing network path, and resolve an authorisation denial. Use when asked why a cloud resource is misbehaving, where a resource lives, why access is denied, or why one service cannot reach another. Strictly read-only.'
allowed-tools: Bash
---

# Cloud Investigation

Read-only investigation of cloud resource behaviour: what a resource is, what
it is attached to, which code owns it, and why it is not behaving.

**Strictly read-only.** Managed infrastructure is code-owned — a CLI mutation
creates drift the next apply reverts or fights, with the reason recorded
nowhere.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Locate Resource | `actions/locate-resource.md` | Prove the identity, find the resource, its relationships and owning code |
| Database Diagnostics | `actions/database-diagnostics.md` | Connection exhaustion, performance, storage, burst credits |
| Network Path | `actions/network-path.md` | Trace source → destination hop by hop, including pod-level identity |
| Access Denied | `actions/access-denied.md` | Simulate the decision; verify identity bindings and key grants |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Read-Only Rules | `standards/read-only-rules.md` | Allowed and forbidden verbs, secret handling, query cost |
| Account Discovery | `standards/account-discovery.md` | Prove identity, resolve profiles, find owning code, live state vs code |
| Checklist | `standards/checklist.md` | Pre-report checks |

## Principles

1. **Prove the identity first** — an investigation in the wrong account
   produces confident, wrong answers.
2. **Read-only; the fix goes to code** — name the owning repo and agent.
3. **Live state over code** — code can be merged and never applied. Drift is
   itself a finding.
4. **Simulate, do not infer** — for authorisation, the simulator beats
   reading policy JSON.
5. **Narrow before querying** — log queries are billed per GB scanned.
6. **Pod identity is not node identity** — dedicated network and IAM
   identities mean node-level rules do not apply.
7. **Secret values are a separate act** — explicit request only, never
   printed, never left on disk.

## Usage

1. Load this manifest and `standards/read-only-rules.md`.
2. Prove the identity and state the region.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md`.
