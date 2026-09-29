#!/usr/bin/env python3
"""One-shot daily observability digest over NerdGraph.

Prints a compact, pre-triaged digest so the agent spends tokens on judgement
rather than on transporting JSON. Read-only: it issues queries and nothing else.

Usage:
  NEW_RELIC_API_KEY=NRAK-... nr-daily.py --account prod=1234567 \
      --account nonprod=7654321 [--region EU] [--hours 1] [--suppress REGEX]...

Exit codes: 0 digest produced (verdict inside), 2 a check could not run.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

ENDPOINT = {"US": "https://api.newrelic.com/graphql",
            "EU": "https://api.eu.newrelic.com/graphql"}


def gql(url, key, query):
    req = urllib.request.Request(url, data=json.dumps({"query": query}).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("API-Key", key)
    try:
        body = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:160].decode(errors='replace')}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    if body.get("errors"):
        return None, "; ".join(str(x.get("message"))[:160] for x in body["errors"][:3])
    return body.get("data"), None


def first_title(t):
    """Issue titles come back as a LIST of incident descriptions, sometimes
    dozens. Keep one line and say how many were folded in."""
    if isinstance(t, list):
        head = t[0] if t else "(untitled)"
        return (head, len(t))
    return (t or "(untitled)", 1)


def num(v):
    """percentile() comes back as {"95": 812.4}, other aggregates as scalars."""
    if isinstance(v, dict):
        vals = [x for x in v.values() if isinstance(x, (int, float))]
        return float(vals[0]) if vals else 0.0
    return float(v) if isinstance(v, (int, float)) else 0.0


def condition_of(title):
    m = re.search(r"on '([^']+)'\s*$", title)
    return m.group(1) if m else ""


def threshold_of(title):
    """'<entity> query result is > 85.0 for 15 minutes on <cond>' -> the middle."""
    m = re.search(r"query result is (.+?) on '", title)
    return m.group(1).strip() if m else ""


def entity_of(title):
    m = re.match(r"(.+?) query result is ", title)
    name = m.group(1).strip() if m else title
    return name.rsplit(":", 1)[-1] if name.startswith("k8s:") else name


def age_str(ms):
    if not isinstance(ms, (int, float)):
        return ""
    h = (time.time() - ms / 1000) / 3600
    if h < 0:
        return ""
    return f"{h:.0f}h" if h < 48 else f"{h / 24:.0f}d"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", action="append", required=True,
                    metavar="ALIAS=ID", help="repeatable; alias 'prod' is treated as production")
    ap.add_argument("--region", default=os.environ.get("NEW_RELIC_REGION", "US"))
    ap.add_argument("--hours", type=int, default=1)
    ap.add_argument("--suppress", action="append", default=[],
                    metavar="REGEX", help="condition names that are known noise")
    ap.add_argument("--error-rate-pct", type=float, default=1.0)
    ap.add_argument("--p95-ms", type=float, default=800.0)
    args = ap.parse_args()

    key = os.environ.get("NEW_RELIC_API_KEY")
    if not key:
        print("NEW_RELIC_API_KEY is not set", file=sys.stderr)
        return 2
    url = ENDPOINT.get(args.region.upper())
    if not url:
        print(f"unknown region {args.region!r}; expected US or EU", file=sys.stderr)
        return 2

    accounts = {}
    for spec in args.account:
        alias, _, aid = spec.partition("=")
        accounts[alias.strip()] = int(aid)
    supp = [re.compile(p, re.I) for p in args.suppress]

    ran = failed = 0
    out = []

    # --- identity: a wrong region returns an EMPTY account, not an error ----
    data, err = gql(url, key, "{ actor { accounts { id name } } }")
    ran += 1
    if err or not data:
        print(f"Verdict:  ⚠️  could not verify — account probe failed: {err}")
        return 2
    visible = {a["id"]: a["name"] for a in data["actor"]["accounts"]}
    missing = [f"{a}={i}" for a, i in accounts.items() if i not in visible]
    if missing:
        print(f"Verdict:  ⚠️  could not verify — not visible in {args.region}: "
              f"{', '.join(missing)}")
        return 2

    # --- open issues, all accounts in ONE request -------------------------
    parts = [f'''{alias}: account(id:{aid}) {{ aiIssues {{
        issues(filter:{{states:[ACTIVATED]}}) {{
          issues {{ issueId title priority createdAt entityNames }}
          nextCursor }} }} }}''' for alias, aid in accounts.items()]
    data, err = gql(url, key, "{ actor { " + " ".join(parts) + " } }")
    ran += 1
    issues, truncated = {}, []
    if err:
        failed += 1
        out.append(("FAIL", "open issues query failed: " + err))
    else:
        for alias in accounts:
            node = data["actor"][alias]["aiIssues"]["issues"]
            if node.get("nextCursor"):
                truncated.append(alias)
            issues[alias] = node["issues"]

    # --- silent entities: reporting=false raises no alerts at all ---------
    parts = [f'''{alias}: entitySearch(query:"accountId = {aid} AND reporting = 'false' AND (domain = 'APM' OR domain = 'BROWSER' OR domain = 'SYNTH')") {{
        count results {{ entities {{ name domain }} }} }}'''
             for alias, aid in accounts.items()]
    data, err = gql(url, key, "{ actor { " + " ".join(parts) + " } }")
    ran += 1
    silent = {}
    if err:
        failed += 1
        out.append(("FAIL", "silent-entity query failed: " + err))
    else:
        for alias in accounts:
            n = data["actor"][alias]
            silent[alias] = (n["count"], [e["name"] for e in n["results"]["entities"]])

    # --- golden signals, now vs same window last week ---------------------
    sig = "SELECT count(*) AS thr, percentage(count(*), WHERE error IS true) AS err, percentile(duration, 95) AS p95 FROM Transaction FACET appName LIMIT 50"
    parts = []
    for alias, aid in accounts.items():
        parts.append(f'''{alias}_now: account(id:{aid}) {{ nrql(query:"{sig} SINCE {args.hours} hours ago") {{ results }} }}''')
        parts.append(f'''{alias}_base: account(id:{aid}) {{ nrql(query:"{sig} SINCE {args.hours + 168} hours ago UNTIL 168 hours ago") {{ results }} }}''')
    data, err = gql(url, key, "{ actor { " + " ".join(parts) + " } }")
    ran += 1
    regressions = {}
    if err:
        failed += 1
        out.append(("FAIL", "golden-signal query failed: " + err))
    else:
        for alias in accounts:
            now = {r["appName"]: r for r in data["actor"][f"{alias}_now"]["nrql"]["results"]}
            base = {r["appName"]: r for r in data["actor"][f"{alias}_base"]["nrql"]["results"]}
            found = []
            for app, cur in now.items():
                b = base.get(app, {})
                e_now, e_base = num(cur.get("err")), num(b.get("err"))
                p_now, p_base = num(cur.get("p95")), num(b.get("p95"))
                t_now, t_base = num(cur.get("thr")), num(b.get("thr"))
                why = []
                if e_now >= args.error_rate_pct and e_now > 2 * max(e_base, 0.05):
                    why.append(f"errors {e_now:.2f}% (base {e_base:.2f}%)")
                if p_now >= args.p95_ms and p_now > 1.5 * max(p_base, 1):
                    why.append(f"p95 {p_now:.0f}ms (base {p_base:.0f}ms)")
                if t_base >= 100 and t_now < 0.5 * t_base:
                    why.append(f"throughput {t_now:.0f} vs {t_base:.0f} baseline")
                if why:
                    found.append((app, "; ".join(why)))
            regressions[alias] = found

    # ------------------------------ report --------------------------------
    act, attn, note, suppressed = [], [], [], 0
    for alias in accounts:
        is_prod = alias.lower().startswith("prod")

        # group issues by alert condition — one chronic condition firing on
        # eight nodes is one finding, not eight
        groups = {}
        for iss in issues.get(alias, []):
            title, folded = first_title(iss.get("title"))
            cond = condition_of(title) or "(no condition)"
            if any(p.search(cond) for p in supp):
                suppressed += folded
                continue
            g = groups.setdefault(cond, {"n": 0, "ents": [], "thr": "",
                                         "prio": "LOW", "oldest": None})
            g["n"] += folded
            g["ents"].append(entity_of(title))
            g["thr"] = g["thr"] or threshold_of(title)
            if iss.get("priority") == "CRITICAL":
                g["prio"] = "CRITICAL"
            c = iss.get("createdAt")
            if isinstance(c, (int, float)) and (g["oldest"] is None or c < g["oldest"]):
                g["oldest"] = c

        for cond, g in sorted(groups.items(), key=lambda kv: -kv[1]["n"]):
            ents = sorted(set(g["ents"]))
            shown = ", ".join(ents[:3]) + (f" (+{len(ents) - 3})" if len(ents) > 3 else "")
            age = age_str(g["oldest"])
            chronic = age and (age.endswith("d") or int(age[:-1] or 0) >= 24)
            bits = [f"{len(ents)} entit{'y' if len(ents) == 1 else 'ies'}"]
            if g["thr"]:
                bits.append(g["thr"])
            if age:
                bits.append(f"oldest {age}" + (" — chronic, likely a threshold to fix" if chronic else ""))
            line = f"[{alias}] {cond} — {'; '.join(bits)}\n      {shown}"
            if is_prod:
                act.append(line)
            elif g["prio"] == "CRITICAL":
                attn.append(line)
            else:
                note.append(line)

        cnt, names = silent.get(alias, (0, []))
        if cnt:
            line = f"[{alias}] {cnt} entit{'y' if cnt == 1 else 'ies'} not reporting — raises no alerts at all\n      {', '.join(names[:4])}"
            if cnt > 4:
                line += f" (+{cnt - 4})"
            (act if is_prod else note).append(line)

        for app, why in regressions.get(alias, []):
            (act if is_prod else attn).append(f"[{alias}] {app}: {why}")

    if failed:
        verdict = "⚠️  could not verify"
    elif act:
        verdict = "🔴 act now"
    elif attn:
        verdict = "🟠 needs attention"
    elif note:
        verdict = "🟡 worth knowing"
    else:
        verdict = "✅ all clear"

    scope = "  ".join(f"{a}={i}" for a, i in accounts.items())
    print(f"Verdict:  {verdict}")
    print(f"Window:   last {args.hours}h vs same window last week   Region: {args.region.upper()}")
    print(f"Accounts: {scope}")
    line = f"Checks:   {ran} ran, {failed} failed"
    if suppressed:
        line += f"  ·  ⚪ {suppressed} suppressed as known noise"
    if truncated:
        line += f"  ·  ⚠️ issues truncated for: {', '.join(truncated)}"
    print(line)
    for sev, msg in out:
        print(f"\n⚠️  {msg}")
    for title, items in (("🔴", act), ("🟠", attn), ("🟡", note)):
        if items:
            print()
            for i in items:
                print(f"{title} {i}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
