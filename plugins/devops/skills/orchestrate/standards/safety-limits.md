# Safety Limits

The floor every agent stands on, regardless of domain. Domain-specific rules
live in each agent's own Boundaries; these five are universal and appear
**verbatim** in every agent, because a limit worded differently in twelve
places is twelve limits.

`scripts/validate.py` fails if an agent is missing one.

## Why the instructions carry the weight

These plugins are general. Whoever installs them supplies their own
credentials, and that is frequently an administrator profile with no
environment separation — because it is what they already had. A design that
relies on the operator having configured a read-only role protects only the
operators who needed protecting least.

So the agent's own discipline is the **primary** mechanism, not a fallback to
one. Write every limit as if the credentials in the session permit anything,
because for many users they will.

That also means an access class — `strict`, `gated`, `mutating` — is a
**declaration of intent, not a capability limit**. A "strictly read-only" agent
holding an administrator profile can delete a production database; nothing in
the class stops it. The class says what the agent has agreed to do.

## The five

```
- 🚫 **Never:** Force-push, or push to `main`, `master`, or `develop` — open a
  pull request instead
- 🚫 **Never:** Run `terraform destroy`, in any environment, targeted or not
- 🚫 **Never:** Widen your own permissions, or edit the settings and hook files
  that define them — that is a human decision, so ask for it
- 🚫 **Never:** Proceed with a change whose plan or diff touches resources
  outside the task — cancel, report what appeared, and ask
- 🚫 **Never:** Assume a command is safe because your remit is read-only — the
  credentials you hold may permit far more than your remit does. Choose read
  verbs deliberately, and if a command's effect is not obvious from its name,
  do not run it
```

## Why these five and not more

Each one is a decision an agent can reach *locally reasonably* and still be
wrong, which is exactly the class of mistake a boundary catches:

- **Force-push and protected branches.** Reconciling a diverged branch by
  force-pushing looks like tidying up. It destroys other people's commits.
- **`terraform destroy`.** Sometimes genuinely the shortest path to a clean
  state, and never the right one from an agent.
- **Self-widening permissions.** An agent blocked by a permission has a
  locally sensible fix available: remove the permission. Every subsequent
  limit depends on it not doing that.
- **Unrelated changes in a plan.** The most dangerous of the five, because it
  arrives disguised as success: the plan applies cleanly, and the change you
  did not ask for goes out with the one you did. Drift, a stale module pin, or
  someone else's half-finished work all show up this way.
- **Credentials exceeding the remit.** A read-only agent given an
  administrator profile has every destructive verb available to it, and no
  error message on the way. "I am the read-only agent" is not a safety
  property; choosing read verbs is.

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

| Layer | Who sets it up | Strength | Blind spot |
|-------|----------------|----------|------------|
| **Agent limits** | **ships with these plugins** | the judgement calls: untargeted apply, a plan exceeding the task, a verb whose effect is unclear | advisory — it holds because the agent read it |
| `permissions.deny` | the operator | absolute, immediate, survives permission modes, splits compound commands | prefix-matched, so argument order and refspecs slip past |
| Server-side branch protection | the operator's forge | rejects a force-push to a protected branch even if everything above fails | nothing outside the forge |
| Cloud IAM | the operator | the only layer an agent cannot talk its way around | assumes roles exist per environment, which is often untrue |

Only the first row travels with the plugins. The other three are worth
recommending and cannot be assumed — which is precisely why the agent limits
have to be written for the case where none of them are in place.

If you are the operator, the deny rules are ten minutes of work and the
read-only role is the strongest single thing you can add. Neither changes what
the agents must already do on their own.
