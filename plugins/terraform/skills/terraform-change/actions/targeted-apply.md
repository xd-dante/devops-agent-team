# Action — Targeted Apply

Apply a plan the user has seen and approved. **This mutates real
infrastructure.**

## Gate — all required

- [ ] A saved plan file from `actions/targeted-plan.md` exists
- [ ] The plan was targeted, and targeting was clean
- [ ] The user has seen the summary and approved **this run**
- [ ] A protected environment, if targeted, was confirmed separately
- [ ] Workspace and cloud identity verified, not assumed

Any box unticked → **🛑 STOP**.

## Apply the saved plan

```bash
terraform apply tfplan
```

Applying the saved file guarantees the user approved exactly what runs.
`terraform apply -target=...` re-plans at apply time and can pick up drift
that appeared in between — only on explicit request.

Never `-auto-approve` a plan the user has not seen.

## If it fails partway

Applies are not transactional. On failure:

1. Do **not** immediately re-run.
2. Capture the error verbatim.
3. Establish what already changed:
   ```bash
   terraform state list | grep -i <target>
   terraform plan -target=<address>     # what remains
   ```
4. Report before acting further. A half-applied change plus a blind retry is
   how state gets corrupted.

## Verify the outcome, not the exit code

```bash
terraform plan -target=<address>        # expect: no changes
```

Then confirm the real-world effect through the owning specialist — the
resource actually created, the policy actually attached, the secret actually
readable. Terraform reporting success is not the same as the system working.

## Report

```
Applied:    <addresses>
Workspace:  <env>        Identity: <account or profile>
Result:     <n> added, <n> changed, <n> destroyed
Re-plan:    clean | <remaining diff>
Verified:   <what was checked downstream, by whom>
Follow-up:  <anything the user must do next>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Re-planning at apply time | Apply the saved plan file |
| `-auto-approve` by default | Only on an approved saved plan |
| Blind retry after partial failure | Inspect state, report, then decide |
| "Apply succeeded" as verification | Re-plan clean plus a downstream check |
| Applying in production on a staging approval | Each environment is its own confirmation |
