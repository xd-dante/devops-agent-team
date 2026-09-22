# Action — Route Task

The default path for a task that is not a full ticket delivery.

## Steps

1. **Restate the ask** in one line. If restating reveals two tasks, treat
   them as two dispatches.

2. **Classify** per `standards/delegation-protocol.md` §1 — goal, domain,
   mutation yes/no, environment. Resolve the domain via
   `standards/routing-table.md`.

   **🛑 STOP** if the domain stays ambiguous, if a mutating task has no
   stated environment, or if a protected environment is the unstated target.

3. **Preflight** the agent's plugin. Missing → use that plugin's hub skill
   directly, or report the gap. Never substitute a nearby specialist.

4. **Dispatch** with a self-contained brief (§2). Announce it in one line:

   ```
   Routing to kubernetes-agent (pod-level triage) and argocd-agent (sync state), in parallel.
   ```

5. **Verify** (§4). Spot-check one factual claim per specialist. Re-dispatch
   with a sharper brief rather than patching a thin report yourself.

6. **Report** once per `standards/report-format.md`, then run
   `standards/checklist.md`.

## Follow-up work

If a finding implies work in another domain — an investigation that found a
Terraform fix, a cost finding needing an infrastructure change — route the
follow-up too. Stop only if it mutates something the user has not approved.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Dispatching before the environment is known | Establish it first; it is the top failure mode |
| "See our earlier discussion" in a brief | Specialists have no history — restate every fact |
| Relaying a report verbatim | Verify, then consolidate |
| Two agents mutating the same target in parallel | Sequence them |
| Doing it yourself because it looked quick | Route it; the specialist carries the standards |
| Swapping in a nearby agent when a plugin is off | Report the gap or use the hub skill |
