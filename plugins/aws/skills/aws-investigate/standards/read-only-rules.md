# Read-Only Rules

## The rule

**This skill reads. It does not change the cloud.** Findings and
recommendations are the output; the change lands through
infrastructure-as-code or is applied by a human.

Managed infrastructure is code-owned. A console or CLI mutation creates drift
that the next apply either reverts or fights, and the reason is recorded
nowhere.

## Allowed — describe, list, get, query

```
sts get-caller-identity
ec2|rds|eks|elbv2|route53   describe-* / list-*
iam                         get-* / list-* / simulate-principal-policy
logs                        describe-* / filter-log-events / start-query
cloudwatch                  get-metric-data / get-metric-statistics / describe-alarms
secretsmanager              describe-secret / list-secrets
s3api                       head-bucket / get-bucket-* / list-objects-v2
ce                          get-cost-and-usage / get-*-recommendation
```

## Forbidden

Anything that creates, modifies, deletes, tags, starts, stops, reboots,
scales, or attaches — including security-group authorize/revoke, parameter
changes, retention changes, and any `--dry-run=false` mutation. Also any
command that writes a profile or credential file.

## Secret values

`describe-secret` (metadata) is routine. Retrieving the **value** is a
different act:

- only on explicit request, for a named secret, with a stated reason
- never printed into the transcript
- never left on the local filesystem — delete any temp file immediately
- **never** retrieved and then used to authenticate to an external system in
  the same flow. Prepare the step and hand the command to the user

## Read-only is not free

Some reads cost money or generate load:

- log-insights queries are billed per GB **scanned**
- wide metric queries with fine periods are expensive
- cost-explorer calls are billed per request
- listing a very large bucket is slow and costly

Scope the window and the resource set before running one. Say what you are
about to scan when it is large.

## Red flags — STOP

- About to run any create/modify/delete verb → recommend instead
- About to retrieve a secret value unprompted → stop
- About to authenticate onward with a credential you just retrieved → hand it
  to the user
- Identity not yet proved → prove it first
- About to scan weeks of logs for a narrow question → narrow it first
