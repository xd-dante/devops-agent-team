# Configuration

No organisation-specific value is hardcoded in this repo. Agents resolve
facts in a fixed order:

1. **`.devops-agents.yml`** at the project root, if present
2. **Runtime discovery** — probe the real system
3. **Ask** — rather than assume

## The config file

Copy [`.devops-agents.example.yml`](../.devops-agents.example.yml) to
`.devops-agents.yml` at the root of the project or workspace you work in.
Every key is optional.

### `tracker`

| Key | Purpose | Discovery fallback |
|-----|---------|--------------------|
| `type` | `jira` \| `github-issues` \| `none` | Ask |
| `base_url` | Ticket URL prefix | Ask |
| `project_key` | Default project for new tickets | Ask |
| `ticket_pattern` | Regex for keys in prose | `[A-Z]+-[0-9]+` |

Field ids (sprint, story points, acceptance criteria) are **discovered per
site** via the tracker's own metadata API, never hardcoded. They differ
between instances.

### `vcs`

| Key | Purpose | Discovery fallback |
|-----|---------|--------------------|
| `branch_template` | Branch naming | `{user}/{type}/{ticket}-{slug}` |
| `commit_style` | `scopeless` \| `scoped` | `scopeless` |
| `pr_title_template` | PR title shape | `{type}: [{ticket}] {summary}` |
| `worktree_layout` | `nested` \| `sibling` \| `none` | `nested` |
| `base_branch_overrides` | Per-repo base branch | Probe `origin/develop`, else `origin/main` |

**On base branches.** Agents probe:

```bash
git fetch origin
git rev-parse --verify --quiet origin/develop >/dev/null && echo develop || echo main
```

They deliberately do **not** trust `origin/HEAD` or
`git remote show origin`. Both cache a value that can be stale or plain wrong
for repos where the integration branch is not the advertised default — a
failure mode that silently targets PRs at the wrong branch. Where the probe
is still wrong, list the repo in `base_branch_overrides`.

### `repos`

Declaring repos is optional but makes cross-repo work reliable: it tells the
orchestrator which repo owns which role, and where submodule edges are.

```yaml
repos:
  - name: example-infra
    role: terraform          # terraform | helm | app | argocd | kargo
    base: develop
    submodules:
      - path: modules/example-module
        repo: example-module
        base: main
```

Without it, agents infer the role from repository contents (`*.tf` →
Terraform, `Chart.yaml` → Helm) and read `.gitmodules` for submodules.

### `environments`

```yaml
environments:
  dev:  { cloud_profile: example-nonprod, cluster: example-platform-dev }
  prod: { cloud_profile: example-prod, cluster: example-platform-prod, protected: true }
```

`protected: true` makes every mutating action require its own confirmation
for that environment, separately from any approval given elsewhere.

Discovery fallbacks:

```bash
kubectl config get-contexts -o name      # clusters
terraform workspace list                 # terraform environments
aws sts get-caller-identity              # which account you are actually in
```

Agents **resolve** a context from this list and switch to it. They never
construct a context name, and never create or repair one — if nothing
matches they stop and report, because authenticating you is not their job.

### `policy`

| Key | Default | Effect |
|-----|---------|--------|
| `terraform_targeted_only` | `true` | Untargeted plan/apply needs per-run approval |
| `cluster_read_only` | `true` | Cluster changes route through GitOps instead |
| `require_pr` | `true` | Never push to a base branch |

Defaults are the safe setting. Turning one off is a deliberate local choice.

## Secrets

This toolkit stores none and asks for none. Agents use the credentials your
shell already has — cloud profile, kubeconfig, `gh` auth, tracker MCP
connection.

Rules the agents follow:

- secret **metadata** is routine; a secret **value** is only fetched on
  explicit request, for a named secret, with a stated reason
- a retrieved value is never printed and never left on disk
- a credential is never retrieved and then used to authenticate onward in the
  same flow — the agent prepares the step and hands you the command

## Keeping the config out of git

`.devops-agents.yml` is gitignored in this repo, and should be gitignored in
yours: it names your hosts, accounts and repositories. Commit the example
file, not the real one.
