# Safety Limits

The floor every agent stands on, regardless of domain. Domain-specific rules
live in each agent's own Boundaries; these four are universal and appear
**verbatim** in every agent, because a limit worded differently in twelve
places is twelve limits.

`scripts/validate.py` fails if an agent is missing one.

## The four

```
- 🚫 **Never:** Force-push, or push to `main`, `master`, or `develop` — open a
  pull request instead
- 🚫 **Never:** Run `terraform destroy`, in any environment, targeted or not
- 🚫 **Never:** Widen your own permissions, or edit the settings and hook files
  that define them — that is a human decision, so ask for it
- 🚫 **Never:** Proceed with a change whose plan or diff touches resources
  outside the task — cancel, report what appeared, and ask
```

## Why these four and not more

Each one is a decision an agent can reach *locally reasonably* and still be
wrong, which is exactly the class of mistake a boundary catches:

- **Force-push and protected branches.** Reconciling a diverged branch by
  force-pushing looks like tidying up. It destroys other people's commits.
- **`terraform destroy`.** Sometimes genuinely the shortest path to a clean
  state, and never the right one from an agent.
- **Self-widening permissions.** An agent blocked by a permission has a
  locally sensible fix available: remove the permission. Every subsequent
  limit depends on it not doing that.
- **Unrelated changes in a plan.** The most dangerous of the four, because it
  arrives disguised as success: the plan applies cleanly, and the change you
  did not ask for goes out with the one you did. Drift, a stale module pin, or
  someone else's half-finished work all show up this way.

## The fourth one is a stop, not a warning

"Flag unexpected destroys" and "cancel when the plan exceeds the task" are
different instructions. Flagging keeps going and leaves the judgement to
whoever reads the report — which, in an unattended seat, is nobody.

Cancel means: do not apply, do not `-auto-approve`, report the resource
addresses that appeared and why you think they are unrelated, and ask. If the
extra changes turn out to be wanted, applying afterwards costs one round trip.
Applying first costs an incident.

Scope the next attempt with `-target` so only the task's resources are in play,
rather than re-running the same broad plan and hoping.

## These are instructions, not enforcement

An agent follows them because it read them. Nothing here stops a determined or
confused agent, and that is worth being clear about rather than implying a
guarantee.

Two stronger mechanisms exist and compose with this, both outside the agent:

| Mechanism | Covers |
|-----------|--------|
| `permissions.deny` in Claude Code settings | absolute prohibitions — `terraform destroy`, force-push, `kubectl delete`. Cannot be overridden by a permission mode |
| Cloud IAM roles | the real boundary. A read-only role for an investigating agent cannot be argued around, and costs it nothing it needs |

A deny rule cannot express the conditional cases — "apply *without* `-target`",
or "a push whose refspec resolves to a protected branch" — because deny beats
allow, so denying `terraform apply*` also blocks the targeted form. Those two
stay judgement calls held here.
