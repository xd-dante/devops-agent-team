#!/usr/bin/env python3
"""Tests for the PreToolUse mutation gate.

Both directions matter. A gate that denies everything is as useless as no gate:
the allow cases below are the work the agents must still be able to do.
"""
import json, pathlib, subprocess, sys

GATE = pathlib.Path(__file__).resolve().parent.parent / "plugins/devops/hooks/gate.py"

MUST_ALLOW = [
    ("terraform plan -target=module.rds -var-file=env/dev.tfvars", "targeted plan"),
    ("terraform apply -target=aws_db_instance.dms -auto-approve",  "targeted apply"),
    ("terraform state list",                                       "state inspection"),
    ("terraform plan -refresh-only",                               "refresh-only"),
    ("kubectl get pods -n smd-dev",                                "cluster read"),
    ("kubectl describe node ip-10-0-1-2",                          "cluster read"),
    ("kubectl logs deploy/api --tail=100",                         "logs"),
    ("kubectl top nodes",                                          "metrics"),
    ("git push -u origin xddante/feat/OPS-1605",                   "feature branch push"),
    ("git commit -m 'feat: thing'",                                "commit"),
    ("helm template . -f values.yaml",                             "chart render"),
    ("argocd app get whitebox-dev",                                "argocd read"),
    ("kargo get freight --project whitebox-cd",                    "kargo read"),
    ("aws rds describe-db-instances --profile x",                  "cloud read"),
    ("rm -rf ./build",                                             "scoped cleanup"),
    # branch names that merely CONTAIN a protected name. A \\b boundary treats
    # "-" and "/" as word edges, so these were wrongly denied at first.
    ("git push -u origin xddante/feat/main-nav",                    "branch containing 'main'"),
    ("git push origin develop-fix",                                 "branch prefixed 'develop'"),
    ("git push origin xddante/fix/master-data",                     "branch containing 'master'"),
    ("git push",                                                    "bare push to upstream"),
]

MUST_DENY = [
    ("terraform apply",                                     "untargeted apply"),
    ("terraform apply -auto-approve",                       "untargeted apply"),
    ("terraform plan",                                      "untargeted plan"),
    ("terraform destroy -target=x",                         "destroy, even targeted"),
    ("terraform state rm aws_db_instance.old",              "state surgery"),
    ("kubectl apply -f manifest.yaml",                      "cluster mutation"),
    ("kubectl delete pod api-1 -n prod",                    "cluster mutation"),
    ("kubectl scale deploy/api --replicas=0",               "cluster mutation"),
    ("kubectl exec -it api-1 -- sh",                        "exec"),
    ("kubectl port-forward svc/api 8080:80",                "port-forward"),
    ("kubectl rollout restart deploy/api",                  "rollout mutation"),
    ("git push --force origin xddante/feat/x",              "force push"),
    ("git push --force-with-lease",                         "force push"),
    ("git push -f origin HEAD",                             "force push short flag"),
    ("git push origin develop",                             "protected branch"),
    ("git push origin HEAD:refs/heads/main",                "protected branch refspec"),
    ("git push origin HEAD:develop",                        "protected branch short refspec"),
    ("git push origin main",                                "protected branch"),
    ("git push --delete origin feat/x",                     "remote branch deletion"),
    ("argocd app sync whitebox-dev",                        "gated sync"),
    ("kargo promote --stage uat --project whitebox-cd",     "gated promotion"),
    ("claude --dangerously-skip-permissions",               "permission bypass"),
    ("codex -s danger-full-access -a never",                "permission bypass"),
    ("rm -rf ~",                                            "home deletion"),
    ("rm -rf /",                                            "root deletion"),
]


def run(tool, command):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    r = subprocess.run([sys.executable, str(GATE)], input=payload,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"gate exited {r.returncode}: {r.stderr}"
    if not r.stdout.strip():
        return "allow", ""
    out = json.loads(r.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"]


def main():
    failures = []
    for cmd, label in MUST_ALLOW:
        d, why = run("Bash", cmd)
        if d != "allow":
            failures.append(f"should ALLOW ({label}): {cmd!r} -> {d}: {why[:70]}")
    for cmd, label in MUST_DENY:
        d, _ = run("Bash", cmd)
        if d != "deny":
            failures.append(f"should DENY ({label}): {cmd!r} -> {d}")

    # a non-Bash tool must fall straight through: editing files is the job
    for tool in ("Edit", "Write", "Read", "Glob"):
        d, _ = run(tool, "")
        if d != "allow":
            failures.append(f"should ALLOW non-Bash tool {tool} -> {d}")

    # a denial must always explain how to proceed
    for cmd, label in MUST_DENY:
        d, why = run("Bash", cmd)
        if d == "deny" and not why.strip():
            failures.append(f"denial with no reason ({label}): {cmd!r}")

    total = len(MUST_ALLOW) + len(MUST_DENY) + 4
    if failures:
        print(f"FAIL — {len(failures)} of {total}")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"gate: {total} cases pass "
          f"({len(MUST_ALLOW)} allow, {len(MUST_DENY)} deny, 4 non-Bash)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
