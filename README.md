# DevOps Agent Team

A team of specialist AI agents for DevOps work, plus an orchestrator that
assigns tasks to them — packaged as [Claude Code](https://code.claude.com)
plugins.

Instead of one general-purpose assistant that knows a bit of everything, you
get **one agent per domain**, each carrying that domain's real operational
rules, and a **manager** that decides who does what.

```
                         ┌──────────────────────┐
        you ─── task ───▶│ devops-orchestrator  │
                         └──────────┬───────────┘
                                    │ routes + briefs + verifies
     ┌──────────┬──────────┬────────┼────────┬──────────┬──────────┐
     ▼          ▼          ▼        ▼        ▼          ▼          ▼
   jira      github    terraform  helm   kubernetes  argocd     kargo
   agent      agent      agent    agent    agent      agent     agent
                                    │
                              aws-investigator · aws-cost
     └──────────┴──────────┴────────┼────────┴──────────┴──────────┘
                                    │
                         one consolidated report ───▶ you
```

## Why an orchestrator

Most "do this DevOps task" requests span several domains. A version that is
wrong in one environment could be a promotion problem, a sync problem, a
chart problem, or a Terraform problem — and the cheapest first check is
different in each case.

The orchestrator holds a **routing table** with those distinctions written
down, so the decision is looked up rather than guessed. It then briefs the
specialist, checks what comes back, and gives you one answer that says which
agent found what.

## Install

```
/plugin marketplace add xd-dante/devops-agent-team
```

Then enable what you need in `settings.json`:

```json
{
  "enabledPlugins": {
    "orchestrator@devops-agent-team": true,
    "jira@devops-agent-team": true,
    "github@devops-agent-team": true,
    "terraform@devops-agent-team": true,
    "kubernetes@devops-agent-team": true
  }
}
```

Project-level `.claude/settings.json` for the stack the whole team works on;
user-level `~/.claude/settings.json` for your personal additions.

Enable `orchestrator` plus whichever specialists match your stack. It reports
a missing plugin rather than silently substituting a different agent.

## The team

| Agent | Plugin | Owns | Mutates? |
|-------|--------|------|----------|
| `devops-orchestrator` | `orchestrator` | Routing, briefing, verification, one report | no |
| `jira-agent` | `jira` | Ticket context, creation, comments, transitions, search | tracker only |
| `github-agent` | `github` | Worktrees, branches, commits, PRs, review rounds, CI | repo only |
| `terraform-agent` | `terraform` | Targeted plans/applies, modules, variables, state | gated |
| `helm-agent` | `helm` | Chart authoring, values, library charts, render debugging | files only |
| `kubernetes-agent` | `kubernetes` | Live cluster investigation | **read-only** |
| `argocd-agent` | `argocd` | Application health, drift, pinned revisions, sync | gated |
| `kargo-agent` | `kargo` | Freight, Warehouses, Stages, promotions | gated |
| `aws-investigator-agent` | `aws` | Why a cloud resource misbehaves | **read-only** |
| `aws-cost-agent` | `aws` | Spend, rightsizing, savings | **read-only** |

AWS is deliberately two agents. "Why is this broken" and "why is this
expensive" use different tools, and conflating them produces bad answers to
both.

## How a task actually runs

Say you hand the orchestrator a ticket:

> work on PROJ-412

```
1. jira-agent          read the ticket — description, acceptance criteria,
                       every attachment, the full comment thread
                       (no ticket id given? it creates one first)
   ↓ 🛑 confirms the understood scope with you before touching anything

2. github-agent        resolve the base branch, create the branch and an
                       isolated worktree, install dependencies

3. domain specialists  terraform-agent / helm-agent / argocd-agent /
                       kargo-agent — whoever owns the files being changed,
                       all working inside that worktree

4. github-agent        commit, push, open the PR, check CI

5. orchestrator        one report: what changed, PR links, merge order,
                       and anything it could not finish
```

Step 1's confirmation gate is deliberate. Restating the scope in different
words is the cheapest way to catch a misread ticket — before any code exists.

The same entry point handles other shapes of work:

| You say | Flow |
|---------|------|
| "work on PROJ-412" | `deliver-ticket` — the full lifecycle above |
| "why is checkout down in staging?" | `incident-triage` — kubernetes + argocd + aws fan out in parallel, read-only, then one root cause |
| "bump the memory limit for the api service" | `route-task` — classify, dispatch to one owner, verify |
| "this value needs to change in two repos" | `cross-repo-change` — classify the value, order the merges |

## How the agents are built

Every agent follows the same four-layer shape. It is what keeps them small
and cheap to run.

```
agents/<name>.agent.md         WHO   role, its own skill list, boundaries
skills/<hub>/SKILL.md          WHICH router: capability → action file
skills/<hub>/actions/<x>.md    HOW   one flow: steps, report shape, mistakes
skills/<hub>/standards/<y>.md  RULES what always applies, + a checklist
```

An agent loads its hub `SKILL.md`, picks **one** action, and loads that action
plus the standards — not the whole domain. So the token cost of a task scales
with the task, not with how much the agent knows.

**Each agent lists its own skills.** Every agent file has a Skills table
mapping a trigger to an action file, so it selects the right sub-skill itself
rather than needing to be told:

```markdown
| When the ask is… | Load |
|------------------|------|
| read a ticket    | actions/read-ticket.md |
| no ticket exists | actions/create-ticket.md |
| record an outcome| actions/update-ticket.md |
```

## How agents talk to each other

Specialists have no shared memory — each starts cold. So handoffs are an
explicit, structured block rather than an assumption:

```
HANDOFF → terraform-agent
objective: raise the connection ceiling for the orders database in staging
context:   max_connections is 110 on the current instance class; peak
           usage hit 108 at 14:20 UTC
scope:     staging only; targeted plan, do not apply
output:    plan summary + whether targeting was clean
```

Two routes, on purpose:

- **Mutations always go back through the orchestrator.** It owns sequencing
  and approval, so agents cannot chain changes between themselves.
- **Read-only questions may go peer to peer**, one hop deep, and must be
  reported. This is what lets `argocd-agent` ask `kubernetes-agent` "are the
  pods actually ready?" without a round trip.

That asymmetry is the whole loop-prevention design: reads can flow sideways,
writes cannot.

## Memory — local, and it learns

Agents keep facts about **your** environment in a local, **gitignored**
memory directory, so they stop re-deriving them and stop making you repeat
corrections.

```
<memory-dir>/
  MEMORY.md          index — one line per entry
  instructions.md    your standing instructions, always loaded
  entries/<slug>.md  one fact per file
```

Resolution order: `$DEVOPS_AGENT_MEMORY` → `<project>/.devops-agents/memory/`
→ `~/.devops-agents/memory/`.

```bash
mkdir -p ~/.devops-agents/memory/entries
cp memory/MEMORY.md.example       ~/.devops-agents/memory/MEMORY.md
cp memory/instructions.md.example ~/.devops-agents/memory/instructions.md
```

| What you say | What happens |
|--------------|--------------|
| nothing — task starts | Standing instructions and relevant entries load |
| "keep in mind…", "from now on…", "never…" | An entry is written |
| you correct the agent | It **offers** to save a rule — showing the exact wording, never saving silently |
| "forget that" | The entry is corrected or deleted |

**`instructions.md` is treated as user instruction**, so it outranks the
agents' own defaults. Put standing rules there:

```markdown
- Never touch production without me saying "production" explicitly.
- Paste plan output in full; do not summarise it.
- Prefer several small PRs over one large one.
```

Memory never leaves your machine. Agents do not quote it into a commit, a PR,
or any file in this repo. A *lesson* from memory can be generalised into a
rule here — mechanism and consequence kept, identifier dropped — but the
entry stays local. Details: [`memory/README.md`](memory/README.md).

## Safety model

The reason to write an agent per domain is that each domain has different
things worth refusing.

- **Read-only agents** declare it in their description, so the orchestrator
  never routes a mutation to one. For the cluster agent, `exec`,
  `port-forward` and `debug` count as mutating — they open sessions that can
  change state.
- **Mutating actions are gated.** They open with a precondition checklist and
  stop if any item is unticked: user approval for *this* run, a stated diff,
  the environment named, production confirmed separately.
- **Protected environments** need their own confirmation. An approval for
  staging is not an approval for production.
- **Terraform is targeted by default.** Untargeted plans and applies need
  per-run approval, because shared state means an untargeted apply can move
  resources nobody asked about.
- **Cluster fixes go through git**, not `kubectl edit`. A live edit to
  something GitOps manages gets reverted, and the reason is recorded nowhere.

Each agent's `Boundaries` section states these as three graded lists —
`✅ Always`, `⚠️ Ask first`, `🚫 Never`.

## Configuration

Nothing about your organisation is hardcoded. Agents work it out in this
order:

1. **`.devops-agents.yml`** at your project root, if present —
   see [`.devops-agents.example.yml`](.devops-agents.example.yml)
2. **Runtime discovery** — probe `origin/develop`, read
   `kubectl config get-contexts`, `terraform workspace list`,
   `aws sts get-caller-identity`
3. **Ask you** — rather than assume

Full key reference and discovery rules: [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md).

That config file is gitignored here. Your hostnames, account ids and repo
names are not this toolkit's business.

## Docs

| Doc | What it covers |
|-----|----------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The four-layer model, routing, handoffs, why it is shaped this way |
| [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) | Config keys and the runtime-discovery fallbacks |
| [`docs/WRITING-AGENTS.md`](docs/WRITING-AGENTS.md) | Adding an agent, a skill, or an action — with the file templates |
| [`CLAUDE.md`](CLAUDE.md) | Instructions for Claude Code working in this repo — the generalisation rule above all |
| [`memory/README.md`](memory/README.md) | The local memory directory: layout, setup, privacy |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Conventions, the review bar, and what not to commit |

## Status

Usable and honest about its limits: these are structured prompts, not tested
software. There is no test runner — validation is mechanical (manifests
parse, frontmatter present, links resolve) plus review. Expect to tune the
agent descriptions against how dispatch actually behaves in your setup.

Contributions welcome, particularly new domain agents and corrections to the
operational rules from people running them in anger.

## License

[MIT](LICENSE) © Pratik Makwana
