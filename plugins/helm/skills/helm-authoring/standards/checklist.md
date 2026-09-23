# Chart Checklist

## Before writing
- [ ] Chart located; whether it delegates to a library chart established
- [ ] The value path classified: static chart value vs computed elsewhere
- [ ] Existing key names read — reuse the chart's vocabulary

## Writing
- [ ] Every new key present in `values.yaml` with a default
- [ ] Environment files carry overrides only, not duplicated blocks
- [ ] `appVersion` bumped if the deployed application version changed
- [ ] Chart `version` bumped per the repo's convention
- [ ] No secret values committed
- [ ] `runAsNonRoot` paired with a numeric uid where set

## Validating
- [ ] `helm lint` clean
- [ ] `helm template` renders for **every** environment values file
- [ ] Rendered output inspected for the field actually in question
- [ ] Multi-document renders diffed semantically, not line by line
- [ ] Library-chart dependency version bumped if the library changed

## Reporting
- [ ] What renders differently, shown from the render
- [ ] Whether a deployment sync is needed for it to take effect
- [ ] Owner named for anything outside the chart
