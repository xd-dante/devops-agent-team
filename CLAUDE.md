# CLAUDE.md

Guidance for Claude Code when working **in this repository**.

## What this repo is

A **public, general-purpose** Claude Code plugin marketplace: specialist
DevOps agents plus an orchestrator that assigns work to them. There is no
build system and no test runner — the "code" is structured Markdown and JSON
interpreted by the harness at install time.

Consumers are other people's organisations. Nothing here may assume ours.

## The one rule that overrides convenience

> **Everything in this repo is generic. Site-specific values are configured
> or discovered at runtime — never written into a file.**

When a change would be easier with a real value hardcoded, that is the moment
the rule matters. Keep the **mechanism and the consequence**; drop the
identifier.

```
✅  "Probe origin/develop — a remote's advertised default branch can be
     stale or wrong, and the failure is silent: the PR targets the wrong
     branch and nobody notices until merge."

🚫  "acme-charts bases on develop even though origin/HEAD says main."
```

### Never commit

- hostnames, URLs, tracker sites, dashboards
- cloud account ids, profile names, ARNs, key ids
- cluster names, namespaces tied to a real deployment
- internal repository names, ticket ids, PR numbers, branch names
- figures from a real invoice, cost report, or capacity plan
- personal names, emails, usernames, absolute home paths
- secrets, tokens, keys, kubeconfigs, `.tfstate`, `.env` — in any form

The only personal values that belong here are the repository owner's
attribution in `LICENSE` and the plugin manifests.

### The generalisation move

When you have a real, specific lesson and want to encode it:

1. Strip the identifier → `<org>`, `<repo>`, `<cluster>`, `<env>`, `<amount>`
2. Keep the mechanism (what the system actually does)
3. Keep the consequence (what breaks, and how it fails — silently or loudly)
4. Put the specific value in `.devops-agents.yml` or runtime discovery

A rule that only makes sense with a real value attached has not been
generalised — it has been redacted, and it will not help anyone.

## Structure

```
.claude-plugin/marketplace.json   Marketplace manifest — every plugin listed
.devops-agents.example.yml        Config template (the real file is gitignored)
scripts/validate.py               Mechanical checks; runs in CI
memory/                           Local memory templates (real entries gitignored)
docs/                             Architecture, configuration, writing agents
plugins/<domain>/
  .claude-plugin/plugin.json      Plugin manifest
  agents/<domain>.agent.md        WHO   — role, skill list, handoffs, boundaries
  skills/<hub>/SKILL.md           WHICH — router: capability → action
  skills/<hub>/actions/<flow>.md  HOW   — one flow: steps, report, mistakes
  skills/<hub>/standards/<rule>.md RULES — always-applies rules + checklist
```

The four-layer split exists so an agent loads a router, picks **one** action,
and loads that action plus the standards — never the whole domain. Token cost
tracks the task, not the size of the domain. Preserve that when editing.

## Adding an agent

Full templates: [`docs/WRITING-AGENTS.md`](docs/WRITING-AGENTS.md). The
short version:

1. `plugins/<domain>/.claude-plugin/plugin.json`
2. `plugins/<domain>/agents/<domain>.agent.md` — frontmatter `name` +
   `description`. Say `PROACTIVELY` and the trigger conditions. **Say
   read-only explicitly if it is** — the orchestrator reads that to decide
   whether a mutation may be routed there
3. `plugins/<domain>/skills/<hub>/SKILL.md` — a router, ~50–80 lines
4. `actions/` — one flow per file, each ending in a report shape and a
   **Common mistakes** table
5. `standards/` — rules, not procedure, plus a `checklist.md`
6. Register in **both**:
   - `.claude-plugin/marketplace.json`
   - `plugins/orchestrator/skills/task-orchestration/standards/routing-table.md`

> An agent absent from the routing table is never dispatched, however good
> its description is. This is the step people forget.

Add a **disambiguation row** too if the new domain overlaps an existing one.
That row is usually worth more than the agent itself.

## Adding a skill or action to an existing agent

- New action → `skills/<hub>/actions/<flow>.md`, plus a row in that skill's
  Capabilities table **and** a row in the agent's own Skills table. An action
  missing from the agent's Skills table will not be found.
- Mutating action → it **must** open with a gate:

  ```markdown
  ## Gate — all required
  - [ ] User approved **this** target and **this** run
  - [ ] The diff or plan was shown first
  - [ ] Environment named; protected environments confirmed separately
  Any box unticked → 🛑 STOP.
  ```

- New rule that applies across actions → `standards/`, not repeated in each
  action.

## House style

- **Tables over prose.** Read more reliably, cost fewer tokens.
- **Name the consequence, not the vibe.** "Auto-sync is off, so merging
  deploys nothing" beats "be careful when syncing".
- **One good/bad example per agent**, showing the failure that domain
  actually produces. Not three.
- **The agent points; the skill holds.** Do not duplicate content between
  them.
- **Hub `SKILL.md` stays a router.** Past ~80 lines, move detail into an
  action.
- Keep `Boundaries` to rules that change behaviour. Twenty bullets nobody
  reads is worse than ten that bite.

## Memory (local, never pushed)

Agents persist org-specific facts to a local memory directory — resolution
order in [`memory/README.md`](memory/README.md). That directory is
**gitignored by design**: it is exactly the material this repo must not
contain.

When working here:

- `memory/*.example` files and `memory/README.md` are committed as templates
- a real `MEMORY.md`, `instructions.md`, or `entries/*.md` is **never**
  committed, and never quoted into a commit message, PR body, doc, or agent
  file
- a lesson learned from memory may be generalised into a rule here — apply
  the generalisation move above first

## Validation

```bash
python3 scripts/validate.py
```

Checks manifests parse, every marketplace `source` resolves, frontmatter is
present, relative links resolve, every routing-table agent exists, no real
memory entries are staged, and no site-specific or credential-shaped strings
are committed. Runs in CI on push and PR.

Then read your own diff as a reviewer would.

## Conventions

- **Commits:** `<type>: <subject>` — **scopeless**, imperative, ≤72 chars.
  Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`.
- **Branches:** `<type>/<short-slug>`
- **PR titles:** `<type>: <2–5 words>` — no leading verb.
- **No AI or assistant attribution** in commits, trailers, PR titles, PR
  bodies, or file content. Author the work as the human.
- Never push to `main` directly if branch protection is on; open a PR.
