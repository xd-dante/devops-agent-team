# Project Profile

One YAML file per tracker project, holding the facts that are stable enough
to cache: ids, issue types, components, teams, defaults, and quirks.

## Where profiles live

Profiles name a real site, cloud id and team ids, so they are **local and
gitignored** — never committed to this toolkit or to the repo being worked
on. First match wins:

| Order | Location |
|-------|----------|
| 1 | `$DEVOPS_AGENT_JIRA_PROJECTS` |
| 2 | `.devops-agents/jira/projects/` — **walk up** from the current directory, like `.devops-agents.yml` |
| 3 | `~/.devops-agents/jira/projects/` |

Walk up rather than using the repo toplevel: the profile directory belongs
at the workspace root, above any one repo, and the toplevel never finds it.

The schema template is `projects/EXAMPLE.yml.example` beside this skill.

## Schema

| Key | Holds | Cacheable because |
|-----|-------|-------------------|
| `schema_version` | `1` | — |
| `verified` | Date the ids were last checked live | Drives the 180-day staleness check |
| `site`, `cloud_id`, `key`, `name`, `board_id` | Project identity | Fixed per site |
| `fields.<role>` | Custom field id per role: `team`, `sprint`, `story_points`, `acceptance_criteria`, `pull_request` | Fixed per site, rarely changed |
| `issue_types.<name>` | `id`, `default`, `sprint: required\|omit`, `acceptance_criteria`, `requires_parent` | Scheme-level |
| `components` | The allowed component vocabulary | Changes by admin action only |
| `teams` | `name`, `id`, `default` | Rarely changes |
| `defaults` | `priority`, `assignee`, `labels`, `content_format` | Team convention |
| `field_rules` | Quirks — see `field-rules.md` | Screen-scheme level |
| `repo_hints` | `ticket_prefix`, `git_remotes` substrings | For key inference |

## Never cache

| Value | Why |
|-------|-----|
| Sprint ids | Sprints roll on a cadence |
| Account ids | Per person, per run |
| Epic keys | Epics open and close |

A profile carrying any of these is wrong — remove the value and look it up
live.
