#!/usr/bin/env python3
"""Daily observability digest — three NRQL/GraphQL queries, aggregated server-side.

Grouping, suppression and baselining are expressed in NRQL so the wire carries
tens of rows instead of thousands of raw incidents. Read-only.

Usage:
  NEW_RELIC_API_KEY=NRAK-... nr-daily.py --account 1234567 --account 7654321 \
      [--region EU] [--prod-env prod] [--hours 1] [--suppress 'condition name']

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
        body = json.loads(urllib.request.urlopen(req, timeout=90).read())
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:160].decode(errors='replace')}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    if body.get("errors"):
        return None, "; ".join(str(x.get("message"))[:160] for x in body["errors"][:3])
    return body.get("data"), None


def esc(q):
    return q.replace('"', '\\"')


def num(v):
    """percentile() returns {"95": 812.4}; other aggregates return scalars."""
    if isinstance(v, dict):
        vals = [x for x in v.values() if isinstance(x, (int, float))]
        return float(vals[0]) if vals else 0.0
    return float(v) if isinstance(v, (int, float)) else 0.0


def age_str(ms):
    if not isinstance(ms, (int, float)):
        return ""
    h = (time.time() - ms / 1000) / 3600
    return "" if h < 0 else (f"{h:.0f}h" if h < 48 else f"{h / 24:.0f}d")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", action="append", required=True, type=int,
                    help="repeatable; queried together in one cross-account NRQL")
    ap.add_argument("--region", default=os.environ.get("NEW_RELIC_REGION", "US"))
    ap.add_argument("--prod-account", type=int, default=None,
                    help="account id treated as production; defaults to the first --account")
    ap.add_argument("--hours", type=int, default=1)
    ap.add_argument("--suppress", action="append", default=[])
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
    accts = "[" + ", ".join(str(a) for a in args.account) + "]"
    ran = failed = 0
    prod_acct = args.prod_account or args.account[0]

    # ---- 0. prove the accounts are visible; a wrong region returns an
    #         EMPTY account rather than an error, which reads as "all clear"
    data, err = gql(url, key, "{ actor { accounts { id name } } }")
    ran += 1
    if err or not data:
        print(f"Verdict:  ⚠️  could not verify — account probe failed: {err}")
        return 2
    visible = {a["id"]: a["name"] for a in data["actor"]["accounts"]}
    missing = [str(a) for a in args.account if a not in visible]
    if missing:
        print(f"Verdict:  ⚠️  could not verify — not visible in "
              f"{args.region.upper()}: {', '.join(missing)}")
        return 2

    # ---- 1. incidents, grouped and suppressed server-side ---------------
    # NrAiIncident is raw incidents. aiIssues groups them, which UNDER-REPORTS:
    # one issue can hide a hundred incidents across as many entities.
    where = ["event = 'open'"]
    for s in args.suppress:
        where.append("conditionName NOT LIKE '%%%s%%'" % s.replace("'", "''"))
    q = ("SELECT uniqueCount(incidentId) AS incidents, "
         "uniqueCount(entity.name) AS entities, latest(priority) AS priority, "
         "earliest(timestamp) AS firstSeen "
         "FROM NrAiIncident WHERE " + " AND ".join(where) +
         " FACET conditionName, account.id "
         f"SINCE {args.hours * 24} hours ago LIMIT 100")
    data, err = gql(url, key,
                    '{ actor { nrql(accounts: %s, query: "%s") { results } } }'
                    % (accts, esc(q)))
    ran += 1
    incidents = []
    if err:
        failed += 1
        print(f"\n⚠️  incident query failed: {err}")
    else:
        incidents = data["actor"]["nrql"]["results"]

    # how many did suppression remove — kept visible on purpose
    suppressed = 0
    if args.suppress and not failed:
        sq = ("SELECT uniqueCount(incidentId) AS n FROM NrAiIncident "
              "WHERE event = 'open' AND (" +
              " OR ".join("conditionName LIKE '%%%s%%'" % s.replace("'", "''")
                          for s in args.suppress) +
              f") SINCE {args.hours * 24} hours ago")
        d2, e2 = gql(url, key,
                     '{ actor { nrql(accounts: %s, query: "%s") { results } } }'
                     % (accts, esc(sq)))
        ran += 1
        if not e2 and d2["actor"]["nrql"]["results"]:
            suppressed = int(d2["actor"]["nrql"]["results"][0].get("n") or 0)

    # ---- 2. golden signals WITH baseline -------------------------------
    # COMPARE WITH returns current and previous rows in ONE query, so the
    # baseline costs no second round trip. Queried per account because
    # account.id comes back NULL on Transaction facets, which would leave a
    # regression unattributable to an environment.
    sig = ("SELECT count(*) AS thr, "
           "percentage(count(*), WHERE error IS true) AS err, "
           "percentile(duration, 95) AS p95 FROM Transaction FACET appName "
           "SINCE %d hours ago COMPARE WITH 1 week ago LIMIT 100" % args.hours)
    parts = ['a%d: account(id:%d) { nrql(query:"%s") { results } }'
             % (a, a, esc(sig)) for a in args.account]
    data, err = gql(url, key, "{ actor { " + " ".join(parts) + " } }")
    ran += 1
    regressions = []
    if err:
        failed += 1
        print("\n(!) golden-signal query failed: %s" % err)
    else:
        for a in args.account:
            cur, base = {}, {}
            for r in data["actor"]["a%d" % a]["nrql"]["results"]:
                f = r.get("facet")
                app = (f[0] if isinstance(f, list) and f else f) or r.get("appName")
                (cur if r.get("comparison") == "current" else base)[app] = r
            for app, c in cur.items():
                b = base.get(app, {})
                e_n, e_b = num(c.get("err")), num(b.get("err"))
                p_n, p_b = num(c.get("p95")), num(b.get("p95"))
                if 0 < p_n < 30:          # this dataset returns seconds
                    p_n, p_b = p_n * 1000, p_b * 1000
                t_n, t_b = num(c.get("thr")), num(b.get("thr"))
                why = []
                if e_n >= args.error_rate_pct and e_n > 2 * max(e_b, 0.05):
                    why.append("errors %.2f%% (base %.2f%%)" % (e_n, e_b))
                if p_n >= args.p95_ms and p_n > 1.5 * max(p_b, 1):
                    why.append("p95 %.0fms (base %.0fms)" % (p_n, p_b))
                if t_b >= 100 and t_n < 0.5 * t_b:
                    why.append("throughput %.0f vs %.0f baseline" % (t_n, t_b))
                if why:
                    regressions.append((app, a, "; ".join(why)))

    # ---- 3. silent entities — NOT expressible in NRQL -------------------
    # An entity that stopped reporting raises no alerts and looks healthy.
    parts = [f'''a{a}: entitySearch(query:"accountId = {a} AND reporting = 'false' AND (domain = 'APM' OR domain = 'BROWSER' OR domain = 'SYNTH')") {{ count results {{ entities {{ name }} }} }}'''
             for a in args.account]
    data, err = gql(url, key, "{ actor { " + " ".join(parts) + " } }")
    ran += 1
    silent = {}
    if err:
        failed += 1
        print(f"\n⚠️  silent-entity query failed: {err}")
    else:
        for a in args.account:
            n = data["actor"][f"a{a}"]
            silent[a] = (n["count"], [e["name"] for e in n["results"]["entities"]])

    # ------------------------------ grade --------------------------------
    act, attn, note, chronic_np = [], [], [], []
    for r in incidents:
        facet = r.get("facet") or []
        cond = facet[0] if facet else "(unknown condition)"
        try:
            aid = int(facet[1]) if len(facet) > 1 else None
        except (TypeError, ValueError):
            aid = None
        n, ents = int(r.get("incidents") or 0), int(r.get("entities") or 0)
        age = age_str(r.get("firstSeen"))
        is_chronic = age.endswith("d") or (age.endswith("h") and int(age[:-1] or 0) >= 24)
        bits = [f"{n} incident{'s' if n != 1 else ''}"]
        if ents:
            bits.append(f"{ents} entit{'y' if ents == 1 else 'ies'}")
        if age:
            bits.append(f"oldest {age}")
        tag = "prod" if aid == prod_acct else "nonprod"
        line = f"[{tag}] {cond} — {'; '.join(bits)}"
        crit = str(r.get("priority") or "").lower() == "critical"
        if aid == prod_acct:
            (act if crit and not is_chronic else attn).append(
                line + (" — chronic, a threshold to fix" if is_chronic else ""))
        elif is_chronic:
            chronic_np.append((cond, n, age))
        elif crit:
            attn.append(("npcrit", cond, n))
        else:
            note.append(("minor", cond, n))

    def label(aid):
        try:
            return visible.get(int(aid), aid)
        except (TypeError, ValueError):
            return "unknown account"

    for app, aid, why in regressions:
        tag = "prod" if aid == prod_acct else "nonprod"
        (act if aid == prod_acct else attn).append("[%s] %s: %s" % (tag, app, why))

    for a, (cnt, names) in silent.items():
        if not cnt:
            continue
        line = (f"[{visible.get(a, a)}] {cnt} entit{'y' if cnt == 1 else 'ies'} "
                f"not reporting — raises no alerts at all\n      "
                + ", ".join(names[:4]) + (f" (+{cnt - 4})" if cnt > 4 else ""))
        (act if a == args.account[0] else note).append(line)

    verdict = ("⚠️  could not verify" if failed else
               "🔴 act now" if act else
               "🟠 needs attention" if attn else
               "🟡 worth knowing" if note else "✅ all clear")

    print(f"Verdict:  {verdict}")
    print(f"Window:   incidents {args.hours * 24}h · signals {args.hours}h vs same window last week · {args.region.upper()}")
    print(f"Accounts: " + "  ".join(f"{a} ({visible.get(a, '?')})" for a in args.account))
    line = f"Checks:   {ran} ran, {failed} failed"
    if suppressed:
        line += f"  ·  ⚪ {suppressed} incidents suppressed as known noise"
    print(line)
    npcrit = [x for x in attn if isinstance(x, tuple)]
    attn = [x for x in attn if not isinstance(x, tuple)]
    if npcrit:
        tot = sum(n for _, _, n in npcrit)
        top = ", ".join(c for _, c, _ in sorted(npcrit, key=lambda x: -x[2])[:4])
        attn.append("[nonprod] %d critical condition(s), %d incidents: %s%s"
                    % (len(npcrit), tot, top, " …" if len(npcrit) > 4 else ""))

    minor = [x for x in note if isinstance(x, tuple)]
    note = [x for x in note if not isinstance(x, tuple)]
    if minor:
        tot = sum(n for _, _, n in minor)
        top = ", ".join(c for _, c, _ in sorted(minor, key=lambda x: -x[2])[:3])
        note.append("[nonprod] %d warning-level condition(s), %d incidents: %s%s"
                    % (len(minor), tot, top, " …" if len(minor) > 3 else ""))

    if chronic_np:
        tot = sum(n for _, n, _ in chronic_np)
        top = ", ".join(c for c, _, _ in sorted(chronic_np, key=lambda x: -x[1])[:3])
        note.append(f"[nonprod] {len(chronic_np)} chronic condition(s), {tot} incidents "
                    f"— thresholds to fix, not incidents: {top}")

    for mark, items in (("🔴", act), ("🟠", attn), ("🟡", note)):
        if items:
            print()
            for i in items[:15]:
                print(f"{mark} {i}")
            if len(items) > 15:
                print(f"{mark} … and {len(items) - 15} more")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
