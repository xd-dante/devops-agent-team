# Field Discovery

**Never hardcode tracker ids.** Site id, project id, board id, and custom
field ids differ between instances and change over time. A hardcoded id is
the most common reason a working ticket flow breaks in someone else's setup.

## Resolve in this order

1. **`.devops-agents.yml`** — `tracker.base_url`, `tracker.project_key`,
   `tracker.ticket_pattern`
2. **The tracker's own metadata API** — for anything id-shaped
3. **Ask the user** — for the project or board when there is a genuine choice

## What must be discovered, not assumed

| Value | How |
|-------|-----|
| Site / cloud id | The tracker's accessible-resources endpoint |
| Project id and issue types | The project's issue-type metadata endpoint |
| Custom field ids (sprint, story points, acceptance criteria) | The create/edit field metadata for that issue type |
| Active sprint | Query the board's sprints — sprints roll on a cadence, so re-query every time |
| Current user | The tracker's own identity endpoint |
| A named assignee | The tracker's user-lookup endpoint — never guess an id |

## Caching within a session

Discovered ids are stable for the life of a session. Resolve once, reuse,
and re-resolve if a call fails with an unknown-field or not-found error
rather than retrying the same id.

## Defaults worth setting once discovered

Reasonable defaults, applied without asking: reporter and assignee are the
current user; team and sprint follow the project's configured defaults;
priority is the project's middle value. Ask only about summary, type,
description, and parent.

Never ask the user for a value you can discover.
