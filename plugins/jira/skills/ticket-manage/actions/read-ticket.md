# Action — Read Ticket

Gather everything needed to implement a ticket. The first step of any
ticket-driven work.

## Step 1 — Fetch the whole issue

Parse the key using the configured pattern (default `[A-Z]+-[0-9]+`). Fetch
the issue with all fields, then read **all** of it:

| Source | Carries |
|--------|---------|
| Summary | A 2–5 word subject — rarely enough on its own |
| Description | What and why |
| **Acceptance criteria field** | The actual definition of done. Frequently not in the description |
| **Attachments** | Screenshots, console output, vendor mail, architecture notes |
| Comments | Where the plan usually changed after creation |
| Linked issues | Dependencies, blockers, duplicates |
| Components / labels | Which part of the estate is in scope |

## Step 2 — Fetch the attachments

**A title is not a specification.** A ticket whose title named one subsystem
has turned out, from its attachment, to be about an entirely different
setting — and the first implementation, written from the title, was wrong.

Retrieve each attachment's content. If one cannot be read, **say so
explicitly** and ask for it rather than proceeding with a gap.

## Step 3 — Read the comments to the end

The most recent comment frequently supersedes the description: a scope cut, a
rejected approach, a decision taken elsewhere. Note where description and
comments disagree.

## Step 4 — Map it onto the repos

Before any implementation: which repos change and in what order, whether a
submodule edge is involved, which environments are targeted, and whether the
change is a static chart value or a computed infrastructure value.

Spans repos → hand the ordering question to the orchestrator's
cross-repo flow.

## Report

```
Ticket:      <KEY> — <summary>
URL:         <tracker-url>/browse/<KEY>
Type:        <type>   Priority: <priority>   Status: <status>
Environment: <env, from the ticket>
Scope (restated):
  <what the work is, in your own words>
Acceptance criteria:
  - <criterion>
Attachments: <n> — <what each one actually said>
Comments:    <any decision that supersedes the description>
Affected repos: <repo(s)>, in order <a → b>
Open questions: <anything genuinely ambiguous>
```

Restating the scope in your own words is the point — it is how a misreading
is caught before code exists.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Implementing from the title | Description, criteria **and** attachments |
| Skipping attachments | They frequently contain the actual requirement |
| Reading only the first comment | The last one often changed the plan |
| Missing the acceptance-criteria field | It is a separate field |
| Filling a gap with an assumption | Name the gap and ask |
| Starting work before restating scope | Confirm first; it is cheap |
