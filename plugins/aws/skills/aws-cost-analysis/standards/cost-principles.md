# Cost Principles

Rules that hold across accounts. No figures here — measure your own.

## 1. Measure before optimising

Run the breakdown first. Optimising something that costs nothing is the
default failure mode of cost work.

## 2. Drill to usage type

A service total is not a finding. `Logs: $X` tells you nothing;
`Logs: ingestion $X vs storage $Y` tells you everything — and points at a
completely different fix.

## 3. Ingestion dwarfs storage

For logs, the money is almost always in **what is emitted**, not how long it
is kept. Retention-reduction recommendations are usually near-worthless and
cost you credibility. Cut emission: sampling, filters, or the component doing
the emitting.

## 4. Attribute, do not assume

Egress and NAT data-processing charges are frequently **not** application
traffic — CI image pulls, package registries, and telemetry exporters are
common causes. Attribute with flow logs before recommending anything.

## 5. Two charges, two fixes

NAT-style services bill for **hours running** and **data processed**
separately. Idle gateways are an hourly-charge fix; volume is a traffic fix.
They are unrelated, and the volume charge is usually the larger number.

## 6. Verify a recommendation against utilisation

Provider rightsizing recommendations use a lookback window that may not
represent steady state. Check the metrics — **average and maximum** — before
acting. A node averaging 8% that peaks at 90% during deploys is not
oversized.

On burstable instance classes, check the credit balance before calling
anything idle.

## 7. Watch for unfiltered exporters

A metric stream or telemetry exporter with no filter exports everything,
continuously. It is a one-line fix with an immediate effect, and it is easy
to miss because nothing is obviously broken.

## 8. Watch for duplicate audit trails

Two overlapping trails recording the same events is pure duplication.
Confirm what reads each before recommending removal.

## 9. Rank by saving per unit of effort

A one-filter change beating a migration worth twice as much is the normal
outcome. Rank that way, not by absolute size.

| Effort | Meaning |
|--------|---------|
| Low | One config value, one filter, tearing down something idle |
| Medium | An infrastructure change with a plan and apply per environment |
| High | Topology change, migration, or application behaviour change |

## 10. State trade-offs inline

Reduced observability, harder queries, commitment risk — inside the
recommendation, not as a footnote. Some savings cost something else.

## 11. Every item has an owner

A recommendation without an owning repo and agent is not routable, so it is
not finished work.

## 12. Never present an estimate as a measurement

Label confidence: measured, estimated, or inferred.
