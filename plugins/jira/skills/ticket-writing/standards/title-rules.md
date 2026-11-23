# Title Rules

Every type: **component or partner name first**, so the title is greppable.
Use a component from the resolved list; never invent one. No trailing
period. ~50 characters is the ceiling — longer means the ticket describes too
much: cut scope or split it.

## Per type

| Type | Length | Verb | Why |
|------|--------|------|-----|
| Story | 2–5 words | **None** | Analyse, build, test, deploy are implicit in a Story — name the outcome |
| Bug / Support | 2–5 words | **None** | Names the fault, not the fix. May lead with the symptom |
| Task | 2–5 words | **Required** | A Task is a discrete action someone executes — name it |
| Epic | 1–3 words | **None** | A heading for a body of work, not a description of it |

## Examples

| Type | ✅ Good | 🚫 Bad |
|------|---------|--------|
| Story | `<Component> node autoscaling` | `Implement autoscaling for <component> nodes` |
| Story | `<Partner> settlement reconciliation` | `Investigate and fix <partner> reconciliation` |
| Bug | `<Database> connection pool exhaustion` | `Fix the connection pool` |
| Task | `Rotate <database> credentials` | `<Database> credential rotation` |
| Epic | `<Partner> Onboarding` | `Onboard the new <partner> integration` |

The verb rule is the one most often broken in both directions: a Story
written as a command, and a Task written as a noun phrase.
