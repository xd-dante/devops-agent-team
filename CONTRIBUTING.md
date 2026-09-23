# Contributing

Contributions welcome — especially new domain agents, and corrections to the
operational rules from people running them for real.

## How to contribute

`main` is protected: it takes pull requests only, and the `validate` check
must pass. You do not need write access — fork and open a PR.

```bash
gh repo fork xd-dante/devops-agent-team --clone
cd devops-agent-team
git checkout -b <type>/<short-slug>
# make the change
python3 scripts/validate.py
gh pr create --base main
```

A few things to expect:

- **Workflows on a fork PR need a maintainer's approval** before they run —
  that is deliberate, not a delay aimed at you
- The workflow token is **read-only** and fork PRs get no repository secrets
- Reviews are requested automatically via `CODEOWNERS`
- History is linear and merges are squashed, so keep the branch rebased on
  `main` rather than merging `main` into it

## Before you open a PR

- Read [`docs/WRITING-AGENTS.md`](docs/WRITING-AGENTS.md) for the file
  templates and house style.
- One domain per PR. A new agent plus unrelated edits to three others is hard
  to review.
- Register a new agent in **both** the marketplace manifest and the
  orchestrator's routing table. An agent missing from the routing table never
  gets dispatched.

## Never commit

This is a public repository. Nothing site-specific belongs in it:

- hostnames, URLs, or tracker sites
- cloud account ids, profile names, ARNs
- cluster names, namespaces tied to a real deployment
- internal repository names, ticket ids, PR numbers
- figures from a real invoice or cost report
- secrets, keys, tokens, kubeconfigs, `.tfstate`, `.env` — in any form

Site-specific values are **configured or discovered** at runtime. If a rule
only makes sense with a real value attached, generalise it: keep the
mechanism and the consequence, drop the identifier.

```
✅  "Probe origin/develop — a remote's advertised default branch can be wrong."
🚫  "helm-charts bases on develop even though origin/HEAD says main."
```

## Conventions

- **Commits:** `<type>: <subject>` — scopeless, imperative, ≤72 chars.
  Types: `feat`, `fix`, `docs`, `refactor`, `chore`.
- **Branches:** `<type>/<short-slug>`
- **PR titles:** `<type>: <2–5 words>` — no leading verb.
- **No AI attribution** in commits, PR titles, PR bodies, or file content.
  Author the work as yourself.

## The review bar

A rule earns its place by naming a real failure. "Always check the base
branch" is advice; "probe `origin/develop`, because a stale advertised
default silently targets PRs at the wrong branch" is a rule. The second gets
followed.

So a PR is likely to be asked for changes if it:

- adds prose where a table would read better
- states an instruction with no consequence attached
- duplicates content between an agent and its skill — the agent points, the
  skill holds
- adds a mutating action without a gate
- pushes a hub `SKILL.md` past ~80 lines instead of moving detail to an action

## Validation

There is no test runner — this is structured Markdown. Before pushing, check
the mechanics:

```bash
# manifests parse
find . -name '*.json' -not -path './.git/*' -exec sh -c 'python3 -m json.tool "$1" >/dev/null' _ {} \;

# every marketplace source resolves, frontmatter present, links resolve
python3 scripts/validate.py
```

Then read your own diff as a reviewer would.
