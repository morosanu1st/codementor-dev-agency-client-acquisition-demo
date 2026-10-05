#!/usr/bin/env python3
"""Dev agency lead pipeline analyzer (Python 3 standard library only).

Reads a CSV of leads and prints:
  1. Pipeline snapshot (leads and value per stage)
  2. Stage-to-stage conversion rates
  3. Weekly outreach targets needed to hit a monthly revenue goal
  4. Stale leads that need a follow-up

Run:  python3 pipeline.py
Help: python3 pipeline.py --help
"""
import argparse
import csv
import math
import sys
from datetime import date, datetime

STAGES = ["Prospect", "Contacted", "Call booked", "Proposal", "Won"]
CLOSED = {"Won", "Lost"}
ALL_STAGES = STAGES + ["Lost"]

# Max days without contact before an open lead is flagged, per stage.
STALE_AFTER_DAYS = {"Contacted": 5, "Call booked": 3, "Proposal": 4}
WEEKS_PER_MONTH = 52 / 12  # ~4.33


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Analyze a dev agency lead pipeline CSV.")
    p.add_argument("--csv", default="data/example_leads.csv", help="Path to leads CSV")
    p.add_argument("--goal", type=float, default=30000, help="Monthly revenue goal (EUR)")
    p.add_argument("--avg-project", type=float, default=None,
                   help="Average project value (EUR). Default: average of Won deals in CSV")
    p.add_argument("--close-rate", type=float, default=0.25,
                   help="Share of conversations (replies) that become won deals, 0-1")
    p.add_argument("--reply-rate", type=float, default=0.10,
                   help="Share of outreach messages that get a reply, 0-1")
    p.add_argument("--today", default=None, help="Override today's date (YYYY-MM-DD)")
    p.add_argument("--stale-days", type=int, default=None,
                   help="Use one stale threshold (days) for all open stages")
    return p.parse_args(argv)


def load_leads(path):
    leads = []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            stage = row["stage"].strip()
            if stage not in ALL_STAGES:
                sys.exit(f"Line {i}: unknown stage '{stage}'. Use one of {ALL_STAGES}")
            lost_at = (row.get("lost_at") or "").strip()
            if stage == "Lost" and lost_at not in STAGES[:-1]:
                sys.exit(f"Line {i}: Lost leads need lost_at = one of {STAGES[:-1]}")
            last = (row.get("last_contact") or "").strip()
            leads.append({
                **row,
                "stage": stage,
                "lost_at": lost_at,
                "value": float(row.get("value_eur") or 0),
                "last_contact": datetime.strptime(last, "%Y-%m-%d").date() if last else None,
            })
    return leads


def furthest_index(lead):
    """Index in STAGES of the furthest stage this lead reached."""
    if lead["stage"] == "Lost":
        return STAGES.index(lead["lost_at"])
    return STAGES.index(lead["stage"])


def conversion_rates(leads):
    reached = [sum(1 for l in leads if furthest_index(l) >= i) for i in range(len(STAGES))]
    rates = []
    for i in range(1, len(STAGES)):
        prev, cur = reached[i - 1], reached[i]
        rates.append((STAGES[i - 1], STAGES[i], prev, cur, cur / prev if prev else 0.0))
    return reached, rates


def weekly_targets(goal, avg_project, close_rate, reply_rate):
    if min(goal, avg_project) <= 0 or not (0 < close_rate <= 1) or not (0 < reply_rate <= 1):
        sys.exit("goal/avg-project must be > 0 and rates must be in (0, 1]")
    deals_month = math.ceil(goal / avg_project)
    convos_month = deals_month / close_rate
    outreach_month = convos_month / reply_rate
    return {
        "deals_month": deals_month,
        "conversations_month": math.ceil(convos_month),
        "outreach_month": math.ceil(outreach_month),
        "deals_week": deals_month / WEEKS_PER_MONTH,
        "conversations_week": math.ceil(convos_month / WEEKS_PER_MONTH),
        "outreach_week": math.ceil(outreach_month / WEEKS_PER_MONTH),
        "outreach_day": math.ceil(outreach_month / WEEKS_PER_MONTH / 5),
    }


def stale_leads(leads, today, override=None):
    out = []
    for l in leads:
        if l["stage"] in CLOSED or l["stage"] == "Prospect":
            continue
        limit = override if override is not None else STALE_AFTER_DAYS[l["stage"]]
        if l["last_contact"] is None:
            out.append((l, None, limit))
            continue
        days = (today - l["last_contact"]).days
        if days > limit:
            out.append((l, days, limit))
    return sorted(out, key=lambda x: -(x[1] if x[1] is not None else 10**6))


def eur(x):
    return f"EUR {x:,.0f}"


def main(argv=None):
    a = parse_args(argv)
    today = datetime.strptime(a.today, "%Y-%m-%d").date() if a.today else date.today()
    leads = load_leads(a.csv)
    if not leads:
        sys.exit("No leads in CSV")

    print(f"=== Lead pipeline report ({today.isoformat()}, {len(leads)} leads from {a.csv}) ===\n")

    print("1) Pipeline snapshot")
    for s in ALL_STAGES:
        group = [l for l in leads if l["stage"] == s]
        print(f"   {s:<12} {len(group):>3} leads   {eur(sum(l['value'] for l in group)):>14}")
    open_value = sum(l["value"] for l in leads if l["stage"] not in CLOSED)
    print(f"   Open pipeline value: {eur(open_value)}\n")

    print("2) Stage conversion rates (leads that reached each stage)")
    reached, rates = conversion_rates(leads)
    for frm, to, prev, cur, r in rates:
        print(f"   {frm:<12} -> {to:<12} {cur:>3}/{prev:<3} = {r:6.1%}")
    print(f"   Overall Prospect -> Won: {reached[-1]}/{reached[0]} = {reached[-1] / reached[0]:.1%}\n")

    won = [l for l in leads if l["stage"] == "Won"]
    avg_project = a.avg_project or (sum(l["value"] for l in won) / len(won) if won else 0)
    if avg_project <= 0:
        sys.exit("No Won deals to estimate --avg-project; pass it explicitly")
    t = weekly_targets(a.goal, avg_project, a.close_rate, a.reply_rate)
    src = "" if a.avg_project else " (avg of Won deals in CSV)"
    print("3) Weekly targets to hit the revenue goal")
    print(f"   Inputs: goal {eur(a.goal)}/month, avg project {eur(avg_project)}{src},")
    print(f"           close rate {a.close_rate:.0%} of conversations, reply rate {a.reply_rate:.0%} of outreach")
    print(f"   Per month: {t['deals_month']} deals <- {t['conversations_month']} conversations"
          f" <- {t['outreach_month']} outreach messages")
    print(f"   Per week:  {t['deals_week']:.1f} deals <- {t['conversations_week']} conversations"
          f" <- {t['outreach_week']} outreach messages (~{t['outreach_day']}/workday)\n")

    print("4) Stale leads needing follow-up")
    stale = stale_leads(leads, today, a.stale_days)
    if not stale:
        print("   None - pipeline is fresh.")
    for l, days, limit in stale:
        age = "never contacted" if days is None else f"{days}d since contact (limit {limit}d)"
        print(f"   [{l['id']}] {l['company']:<26} {l['stage']:<12} {age:<32} -> {l['next_step']}")
    print(f"\n   {len(stale)} lead(s) flagged. Thresholds: "
          + (f"{a.stale_days}d for all stages" if a.stale_days is not None
             else ", ".join(f"{k} {v}d" for k, v in STALE_AFTER_DAYS.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
