---
name: terraform-workflow
description: 'Execute Terraform work safely — orient in a stack, produce a targeted plan, apply an approved plan, change a module or variable, and run state operations. Use when asked to plan or apply Terraform, add or change infrastructure resources, wire a value through a module, fix HCL, work with workspaces and variable files, or import/move/remove state. Enforces targeted plans and applies.'
allowed-tools: Bash
---

# Terraform Workflow

Infrastructure-as-code work, with the safety rules shared state demands: many
components per state, drift in resources nobody asked about, and applies that
are not transactional.

**The defining rule: every plan and apply is `-target`ed.** An untargeted run
needs explicit per-run approval.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Inspect Stack | `actions/inspect-stack.md` | Repo, base branch, workspaces, submodules, value path |
| Targeted Plan | `actions/targeted-plan.md` | Plan only the intended resources; say whether targeting was clean |
| Targeted Apply | `actions/targeted-apply.md` | **Gated.** Apply a saved approved plan and verify the outcome |
| Module Change | `actions/module-change.md` | Variables, resources, outputs, submodule mechanics |
| State Operations | `actions/state-operations.md` | **Gated.** import, state rm, state mv, -replace |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Safety Protocol | `standards/safety-protocol.md` | Targeting rule, plan review, environment proof, ask-first and never lists |
| HCL Style | `standards/hcl-style.md` | Shape in the variable type; banned constructs; comment limits |
| Checklist | `standards/checklist.md` | Pre-commit and pre-apply checks |

## Principles

1. **Targeted, always** — shared state means an untargeted apply can move
   resources the task never mentioned.
2. **Shape belongs in the variable** — `optional(..., default)` in the type,
   not `try()` in the resource.
3. **Plan files are contracts** — apply the plan the user approved, not a
   fresh one.
4. **Prove the environment** — cloud identity and workspace, before anything.
   `workspace select` can silently no-op.
5. **Code carries purpose, not history** — rationale lives in the commit, PR
   or README.
6. **Terraform success is not system success** — verify the downstream effect.

## Usage

1. Load this manifest and `standards/safety-protocol.md`.
2. Run `actions/inspect-stack.md` unless the stack is already established.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md`.
