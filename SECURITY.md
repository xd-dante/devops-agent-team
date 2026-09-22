# Security Policy

## Scope

This repository contains **prompts and documentation** — structured Markdown
and JSON interpreted by an AI coding harness. It ships no executable service.
The only code is `scripts/validate.py`, a local and CI validation helper.

That said, these files **instruct an agent that runs commands against real
infrastructure**. So the security surface that matters here is the
instructions themselves.

## What counts as a vulnerability

Please report:

- an instruction that could lead an agent to **exfiltrate a secret** — for
  example, printing a credential value, writing one to disk, or sending one
  to a third party
- an instruction that could cause **destructive infrastructure action**
  without the gate that should precede it
- a **missing or bypassable gate** on a mutating action
- a path by which **site-specific data** (accounts, hostnames, tickets)
  could be committed to this public repository
- anything in the repository history that **already leaks** such data
- a supply-chain concern in the GitHub Actions workflow

## What does not

- An agent making a wrong technical judgement inside its stated boundaries.
  That is a bug — open an issue.
- A missing capability, or a rule you disagree with. Open an issue or a PR.

## Reporting

Use **GitHub's private vulnerability reporting** on this repository
(Security → Report a vulnerability). That keeps the report private until a
fix is out.

Please do not open a public issue for anything involving leaked data.

Include: the file and line, what an agent would do as a result, and the
consequence. A proposed rewording is very welcome — most fixes here are a
wording change.

Expect a first response within a week. This is a personal project, so there
is no formal SLA beyond that.

## Secrets in this repository

There should be none, ever. Nothing here needs a credential: agents use
whatever your shell is already authenticated with.

`scripts/validate.py` scans for credential-shaped and site-specific strings
on every push and pull request, and secret scanning with push protection is
enabled. If you believe something slipped through the history, report it
privately rather than opening an issue.

## Using this toolkit safely

- Enable only the plugins you need.
- Keep `policy.*` in `.devops-agents.yml` at its safe defaults — targeted
  applies, read-only clusters, PRs required.
- Mark production environments `protected: true` so every mutating action
  needs its own confirmation.
- Keep your memory directory gitignored. It is site-specific by design.
- Read what an agent proposes before approving it. The gates exist so that a
  human decision sits in front of anything irreversible.
