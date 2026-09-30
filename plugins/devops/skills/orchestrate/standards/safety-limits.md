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

## The deny list, and what it actually covers

Verified behaviour, not documentation reading:

- deny rules take effect **immediately** — no restart
- deny beats allow, so `Bash(*)` in `allow` does not weaken them
- **compound commands are split and each part checked** — `true && <denied>`
  is denied, and so is a denied command buried in a longer script

A starting list for an infrastructure repo:

```jsonc
"permissions": {
  "deny": [
    "Bash(terraform destroy:*)",  "Bash(tofu destroy:*)",
    "Bash(terraform state rm:*)", "Bash(terraform state push:*)",

    "Bash(git push --force:*)",   "Bash(git push --force-with-lease:*)",
    "Bash(git push -f:*)",        "Bash(git push origin --force:*)",
    "Bash(git push --delete:*)",  "Bash(git push origin --delete:*)",

    "Bash(git push origin main:*)",    "Bash(git push origin master:*)",
    "Bash(git push origin develop:*)",

    "Bash(kubectl delete:*)", "Bash(kubectl drain:*)", "Bash(kubectl replace:*)",

    "Bash(claude config set -g permissions:*)"
  ]
}
```

### Three gaps, measured

**Matching is by prefix, so argument order matters.** With a rule denying
`echo denytest`, the command `echo --quiet denytest` runs: the denied token is
no longer at the start. So `git push origin feat/x --force` is **not** caught
by `Bash(git push --force:*)`. Listing orderings helps and does not close it.

**A refspec is opaque to a prefix rule.** `git push origin HEAD:refs/heads/main`
matches no rule naming `main` as an argument.

**`terraform apply` without `-target` cannot be denied at all.** Deny beats
allow, so denying `Bash(terraform apply:*)` also blocks the targeted form that
is the whole point. This one has to stay a judgement call in the agent.

### What each layer is actually for

| Layer | Strength | Blind spot |
|-------|----------|------------|
| Agent limits | catches the judgement calls: untargeted apply, a plan exceeding the task | advisory — it holds because the agent read it |
| `permissions.deny` | absolute, immediate, survives permission modes, splits compound commands | prefix-matched, so argument order and refspecs slip past |
| Server-side branch protection | rejects a force-push to a protected branch even if everything above fails | nothing outside the forge |
| Cloud IAM | the only layer an agent cannot talk its way around | needs roles set up per environment |

No single layer is sufficient, and the top two are the weakest. If only one
thing gets done, make it the IAM read-only role for the investigating agents.
