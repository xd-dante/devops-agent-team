# Action — Resolve Project

Produce the create envelope for one project and one issue type.

## Step 1 — Resolve the project key

| Signal | Use |
|--------|-----|
| Key explicit in the request, or a ticket key like `<KEY>-123` | Wins outright |
| Current branch name | First match of `tracker.ticket_pattern` |
| `git log --oneline -50` | First ticket prefix found |
| `git remote -v` | Match against each profile's `repo_hints.git_remotes` |
| `tracker.project_key` in `.devops-agents.yml` | Default when nothing above matched |

**Confirm an inferred key with the user** before going on. Several distinct
prefixes in the log, or no signal at all → ask; do not pick one.

## Step 2 — Load the profile

Find `<KEY>.yml` per `standards/project-profile.md`. Not found →
`actions/bootstrap-project.md`, then come back to Step 3.

`verified` older than 180 days → still use it, but re-check the fields this
run touches (Step 6 of the bootstrap action, scoped) and report drift.

## Step 3 — Live lookups

Never read these from a profile. They change too often to cache.

| Value | How |
|-------|-----|
| Assignee | The tracker's current-user endpoint, unless the user named someone — then the user-lookup endpoint. Never guess an account id |
| Active sprint | Skip when `issue_types.<type>.sprint` is `omit`. Otherwise search `project = <KEY> AND sprint in openSprints() ORDER BY created DESC`, `maxResults: 1`, requesting the profile's sprint field; take the sprint whose state is `active` |
| Epic candidates | Only when a parent is wanted and none was named: `project = <KEY> AND issuetype = Epic AND statusCategory != Done ORDER BY updated DESC`, `maxResults: 25` |

No active sprint for a type that requires one → surface it and ask. Do not
invent a sprint id.

Sub-task (`requires_parent: true`) with no parent given → ask for it.

## Step 4 — Apply field rules

Walk `field_rules` per `standards/field-rules.md`. Collect each applied
rule's `user_note` into `notes`.

## Step 5 — Return the envelope

```yaml
project: { key: <KEY>, name: <name>, site: <site> }
content_constraints:
  components: [...]                 # the only allowed vocabulary for titles
  issue_types: [...]
  acceptance_criteria: <true|false> # for the resolved issue type
  duplicate_search_jql_template: 'project = <KEY> AND statusCategory != Done AND summary ~ "{TERMS}"'
epic_candidates: [ { key, summary } ]   # only if looked up
notes: [ "<user_note from applied field rules>" ]
create_call:
  tool: createJiraIssue               # the tracker MCP's create tool, whatever its prefix
  args:
    cloudId: <cloud_id>
    projectKey: <KEY>
    issueTypeName: <type>
    contentFormat: <defaults.content_format>
    assignee_account_id: <resolved>
    summary: "<<FILL: summary>>"
    description: "<<FILL: description>>"
    parent: "<<FILL_OPTIONAL: parent>>"
    additional_fields:
      priority: { name: <defaults.priority> }
      <fields.team>: <team id>
      <fields.sprint>: <sprint id>     # absent when sprint is omit for the type
      labels: <defaults.labels>
```

The MCP tool prefix depends on how the tracker server was installed (plugin,
connector, or local server). Match the tool on its base name.

## Report

The envelope above, plus one line:

```
Resolved: <KEY> (<source: explicit | branch | log | remote | config>, confirmed) — profile verified <date>, sprint <name | omitted>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Acting on an inferred key silently | Confirm it with the user |
| Reading a sprint or account id from the profile | Always live |
| "Fixing" a quirk beyond its `action` | Apply it literally |
| Handing back raw field ids for the caller to place | Return a filled `create_call` |
| Inventing a sprint when none is active | Surface it and ask |
| Hardcoding the MCP tool prefix | Match on the base tool name |
