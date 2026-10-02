# Action — Findings Inventory

Who aggregates what, which standards are on, and where the finding volume
really comes from.

## Step 1 — Topology

```bash
aws securityhub describe-hub                        # subscribed? control finding generator?
aws securityhub get-administrator-account           # am I a member?
aws securityhub list-members --only-associated      # am I the administrator?
aws securityhub list-finding-aggregators            # cross-region aggregation?
aws securityhub get-enabled-standards --query 'StandardsSubscriptions[].[StandardsArn,StandardsStatus]'
aws securityhub list-enabled-products-for-import    # which services feed findings in
```

- **The administrator sees every member's findings.** Split all counts by
  `AwsAccountId`.
- Probe each enabled region. An organisation policy deny returns an explicit
  error, not an empty list. Record it as **blocked**, not as zero.
- Compare enabled standards with the infrastructure code. A standard enabled
  in the console is drift, and it raises volume without anyone having
  decided to.

## Step 2 — Pull once, project early

A full pull can be tens of MB and take many minutes. Pull to a file once.

```bash
aws securityhub get-findings --filters '{
  "RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}],
  "WorkflowStatus":[{"Value":"NEW","Comparison":"EQUALS"},{"Value":"NOTIFIED","Comparison":"EQUALS"}]
}' --output json > findings.json

jq -r '.Findings[] | [.Id, .AwsAccountId, .Severity.Label, .ProductName,
  (.Compliance.SecurityControlId // .GeneratorId), .Resources[0].Type,
  .Resources[0].Id, .Title] | @tsv' findings.json > findings.tsv
jq -r '.Findings[].Id' findings.json | sort -u > active-ids.txt
```

If you only need ids (for example, re-checking staleness later), add
`--query 'Findings[].Id' --output text`. That removes most of the payload.

## Step 3 — Aggregate

```bash
cut -f3 findings.tsv | sort | uniq -c | sort -rn          # by severity
cut -f4 findings.tsv | sort | uniq -c | sort -rn          # by product
cut -f2,3 findings.tsv | sort | uniq -c                   # by account × severity
awk -F'\t' '{print $5"\t"$8}' findings.tsv | sort | uniq -c | sort -rn | head -25   # top controls
cut -f5,7 findings.tsv | sort -u | cut -f1 | uniq -c | sort -rn | head   # distinct resources per control
```

## Step 4 — Name the noise generators

Check `standards/finding-sources.md` and flag each pattern that applies.
Common ones:

- patch-compliance findings re-issued on every scan run, so thousands of
  findings trace back to a few instances
- ephemeral compute, with one finding per short-lived instance
- a tagging standard failing on platform-created resources

For each, report the finding count **and** the distinct resource count, and
how many of those resources still exist.

## Report (feeds section 2 and 4 of the full report)

```
Administrator: <acct>   Members: <acct…>   Aggregator: <none | region>
Regions: in scope <…>  blocked <…>  not subscribed <…>
Standards: live <…>  in code <…>  drift <…>
Totals: by severity, by product, by account × severity
Top controls: control | title | severity | findings | distinct resources
Noise generators: pattern | findings | distinct resources | resources still existing
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| One total across administrator and members | Split by account |
| A denied region reported as clean | Report it as blocked |
| Counting findings for ephemeral compute | Count distinct resources, and how many still exist |
| Re-pulling the full payload for every question | Pull once, project to TSV |
