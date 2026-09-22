# Action — Search Tickets

Find tickets by state, assignee, sprint or content — for duplicate checks,
roundups, and "has this been looked at before".

## Step 1 — Search the subject noun

Titles are deliberately terse, so a sentence from the request will not match.
Search the noun.

## Step 2 — Useful queries

```
-- my open work
project = <KEY> AND assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC

-- current sprint
project = <KEY> AND sprint in openSprints() ORDER BY status ASC

-- a specific area
project = <KEY> AND component = <component> AND statusCategory != Done

-- recently closed: "was this already fixed?"
project = <KEY> AND statusCategory = Done AND resolved >= -30d ORDER BY resolved DESC

-- free text, including comments
project = <KEY> AND text ~ "<subject noun>" ORDER BY updated DESC

-- blocked work
project = <KEY> AND issueLinkType = "is blocked by" AND statusCategory != Done
```

## Step 3 — Read before reporting

A hit list is not an answer. Fetch each relevant hit and check it actually
covers the question — terse titles mean a keyword match is not a content
match.

## Report

```
Query:    <the query>
Hits:     <n>
Relevant:
  - <KEY> <status> — <summary>  → <why it matters here>
    <tracker-url>/browse/<KEY>
Duplicate risk: <existing ticket, or none found>
```

State "none found" explicitly. A silent empty result reads like the search
never ran.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Searching with the request's own phrasing | Search the subject noun |
| Reporting a hit list without reading the tickets | Verify relevance per hit |
| Omitting the closed-ticket check | "Already fixed" is a common answer |
| Not saying when nothing matched | State "none found" |
| Ignoring issue links | Blockers and duplicates live there |
