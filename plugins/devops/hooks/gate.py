#!/usr/bin/env python3
"""PreToolUse gate — deterministic limits on destructive commands.

Why this exists: an agent's Boundaries section is prose, and prose is advice.
Interactively the real gate is the permission prompt, answered by a human. An
unattended seat has no human at its terminal, so a prompt either blocks the
seat forever or gets allowlisted away. This hook decides without anyone
present.

It does NOT restrict file edits. Writing Terraform, charts and code is the
job. What it refuses is the small set of commands that change live systems or
rewrite shared history.

A denial is not a dead end: the reason tells the agent to escalate, which
surfaces the decision to a human through the orchestrator.

Contract: reads the PreToolUse payload on stdin, prints a permissionDecision.
Exit code is always 0 — a crashing gate must not look like a denial, and a
silent failure must not look like an allow, so unparseable input asks.
"""
import json
import re
import shlex
import sys

GUARDED = ("settings.json", "settings.local.json", "hooks.json", "gate.py",
           "permissions.defaultmode")


def _is_guarded(path: str) -> bool:
    return any(g in path.lower() for g in GUARDED)


def _writes_guarded_file(command: str) -> bool:
    """True only when a write mechanism TARGETS a guarded file.

    Co-occurrence is not enough: `python3 tests/test_gate.py > /tmp/out` names
    a guarded file and redirects, but writes somewhere harmless.
    """
    low = command.lower()

    # shell redirection: inspect the target that follows > or >>
    for m in re.finditer(r">>?\s*([^\s;|&]+)", command):
        if _is_guarded(m.group(1)):
            return True

    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    # commands whose file arguments are the thing being changed
    mutators = {"tee", "rm", "mv", "truncate", "chmod", "chown", "dd", "install", "ln"}
    for i, t in enumerate(tokens):
        base = t.rsplit("/", 1)[-1]
        if base in mutators and any(_is_guarded(a) for a in tokens[i + 1:] if not a.startswith("-")):
            return True
        if base in {"sed", "perl", "gsed"} and "-i" in tokens[i + 1:]:
            if any(_is_guarded(a) for a in tokens[i + 1:] if not a.startswith("-")):
                return True

    # inline interpreters can write anything; if a guarded name appears in the
    # program text, refuse rather than trying to read the code
    if re.search(r"(python3?|node|ruby|perl)\s+-c\b", low) and _is_guarded(low):
        return True

    # `claude config set ... permissions.defaultMode ...`
    if "config set" in low and "permissions.defaultmode" in low:
        return True
    return False


PROTECTED = {"develop", "main", "master"}


def _push_destinations(command: str) -> list[str]:
    """Destination refs of a `git push`, normalised to a bare branch name.

    A bare `git push` names no ref; server-side branch protection remains the
    backstop for that case, and refusing it would block ordinary feature-branch
    work in an unattended seat.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if "push" not in tokens:
        return []
    rest = tokens[tokens.index("push") + 1:]
    args, skip = [], False
    for t in rest:
        if skip:
            skip = False
            continue
        if t in ("-o", "--push-option", "--repo", "--receive-pack", "--exec"):
            skip = True
            continue
        if t.startswith("-"):
            continue
        args.append(t)
    refspecs = args[1:] if len(args) > 1 else []
    out = []
    for spec in refspecs:
        dst = spec.split(":", 1)[1] if ":" in spec else spec
        dst = dst.strip().removeprefix("+").removeprefix("refs/heads/")
        if dst:
            out.append(dst.rsplit("/", 1)[-1] if dst.startswith("refs/") else dst)
    return out


ALLOW, DENY, ASK = "allow", "deny", "ask"


def decide(command: str):
    """Return (decision, reason) for a Bash command string."""
    c = " ".join(command.split())
    low = c.lower()

    # --- permission bypass: never, by any route -------------------------
    # `low` is whitespace-normalised and lowercased, so one spelling per form
    # covers bypassPermissions / BYPASSPERMISSIONS and friends.
    for flag in (
        "--dangerously-skip-permissions",
        "--dangerously-bypass-approvals-and-sandbox",
        "danger-full-access",
        "--yolo",
        "openrig_yolo=1",
        "--permission-mode bypasspermissions",
        "--permission-mode=bypasspermissions",
        "--ask-for-approval never",
        "--ask-for-approval=never",
    ):
        if flag in low:
            return DENY, (
                f"{flag} removes tool-permission checks for the rest of the "
                "session. If a command genuinely needs broader access, escalate "
                "to the orchestrator and let a human grant it explicitly.")
    # codex short form: -a never
    if re.search(r"(?<![\w-])-a\s+never(?![\w-])", low):
        return DENY, (
            "-a never disables approval prompts for the rest of the session. "
            "Escalate instead of removing the checks.")

    # --- do not disarm the gate itself -----------------------------------
    # The gate only sees Bash, so a command that rewrites the permission config
    # or removes the hook would defeat every rule below it. Reading these files
    # stays allowed, and so does redirecting unrelated output — only a write
    # whose TARGET is a guarded file is refused.
    if _writes_guarded_file(c):
        return DENY, (
            "this command writes to the permission configuration or the gate "
            "hook itself. Changing what an agent is allowed to do is a human "
            "decision — escalate and say what access is needed and why.")

    # --- terraform -------------------------------------------------------
    if re.search(r"\bterraform\b", low) or re.search(r"\btofu\b", low):
        if re.search(r"\b(destroy)\b", low):
            return DENY, (
                "terraform destroy is never run by an agent. If teardown is the "
                "actual goal, escalate with the resource list so a human runs it.")
        if re.search(r"\b(apply|plan)\b", low) and "-target" not in low:
            # -refresh-only and state inspection are not changes
            if not re.search(r"-refresh-only|\bstate\s+(list|show|pull)\b", low):
                return DENY, (
                    "untargeted terraform apply/plan is not permitted — it can act "
                    "on resources outside the change. Re-run with -target=<addr> "
                    "for the resources this task owns. If the blast radius is "
                    "genuinely the whole stack, escalate and say so.")
        if re.search(r"\bstate\s+(rm|mv|push|replace-provider)\b", low):
            return DENY, (
                "terraform state surgery rewrites shared state and is not "
                "reversible from here. Escalate with the exact command and why.")

    # --- kubernetes: desired state lives in git --------------------------
    if re.search(r"\bkubectl\b", low):
        mutating = (r"\b(apply|create|delete|patch|replace|edit|scale|annotate|"
                    r"label|cordon|uncordon|drain|taint|set|exec|attach|cp|"
                    r"port-forward|proxy)\b")
        if re.search(mutating, low):
            return DENY, (
                "cluster changes go through GitOps, not kubectl. Read freely "
                "(get/describe/logs/events/top). To change desired state, hand "
                "off to the agent that owns the manifest or chart. An ephemeral "
                "debug container is a gated flow — escalate for it.")
        if re.search(r"\brollout\s+(restart|undo|pause|resume)\b", low):
            return DENY, (
                "rollout mutations are a cluster change — route the fix to the "
                "repo that owns desired state.")

    # --- git: protected branches and history rewrites ---------------------
    if re.search(r"\bgit\b", low) and re.search(r"\bpush\b", low):
        if re.search(r"(--force\b|--force-with-lease|(?<![\w-])-f(?![\w-]))", c):
            return DENY, (
                "force-push is not permitted. If the branch diverged, branch "
                "again from a fresh base and redo the change.")
        if "--delete" in low:
            return DENY, "remote branch deletion is not permitted from an agent."
        # Parse the refspec rather than substring-matching the branch name:
        # a \b boundary treats "-" and "/" as word edges, so "feat/main-nav"
        # and "develop-fix" would both look like protected branches.
        for dst in _push_destinations(c):
            if dst in PROTECTED:
                return DENY, (
                    f"{dst} is branch-protected — push a feature branch and open "
                    "a pull request instead.")

    # --- delivery tools whose mutation is a gated flow --------------------
    if re.search(r"\bargocd\b", low) and re.search(r"\b(sync|delete|set|rollback|terminate-op)\b", low):
        return DENY, (
            "an Application sync is a gated single-app action. Report what would "
            "change and escalate; do not sync unprompted.")
    if re.search(r"\bkargo\b", low) and re.search(r"\b(promote|delete|approve)\b", low):
        return DENY, (
            "a Stage promotion is a gated action. Report the Freight and what it "
            "would move, then escalate.")

    # --- blunt filesystem destruction ------------------------------------
    if re.search(r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)\b", low):
        try:
            parts = shlex.split(c)
        except ValueError:
            parts = c.split()
        targets = [p for p in parts if not p.startswith("-") and p not in ("rm", "sudo")]
        if any(t in ("/", "~", "$HOME", "/*", ".", "./") for t in targets):
            return DENY, "recursive force delete of a home or root path is refused."

    return ALLOW, ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        emit(ASK, "gate could not parse the tool payload; asking rather than assuming")
        return 0

    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}

    if tool != "Bash":
        # File edits are the job. Everything non-Bash falls through untouched.
        return 0

    command = tool_input.get("command") or ""
    if not command:
        return 0

    decision, reason = decide(command)
    if decision != ALLOW:
        emit(decision, reason)
    return 0


def emit(decision: str, reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


if __name__ == "__main__":
    sys.exit(main())
