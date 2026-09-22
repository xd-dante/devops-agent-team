# Cost Checklist

## Before analysing
- [ ] Identity proved; profile matches the account
- [ ] Period stated explicitly, with granularity
- [ ] Pre- or post-tax established, and the metric named
- [ ] Query set planned — cost-explorer calls are billed per request

## Analysing
- [ ] Started top-down: total → service → usage type → resource
- [ ] Ingestion separated from storage for anything log-related
- [ ] Data transfer attributed to a real source, not assumed
- [ ] Anything already known-clean re-verified rather than re-reported

## Recommending
- [ ] Every item carries a monthly figure and a confidence label
- [ ] Every item carries effort and risk
- [ ] Ranked by saving per unit of effort, not absolute size
- [ ] Owning repo and agent named per item
- [ ] Anything reducing observability or resilience says so

## Reporting
- [ ] Total, addressable, and recommended-now stated separately
- [ ] Assumptions and lookback windows stated
- [ ] Explicit statement that nothing was mutated
