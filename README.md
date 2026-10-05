# Dev Agency Client Acquisition Demo

A small, practical toolkit for a software development agency (web, software, UX/UI, mobile, SaaS, AI automation) that wants a **repeatable system for getting steady clients** instead of relying on luck and word of mouth.

It contains:

- **`pipeline.py`** — a dependency-free Python 3 tool that reads a lead CSV and reports:
  - pipeline snapshot per stage (Prospect → Contacted → Call booked → Proposal → Won/Lost)
  - stage-to-stage conversion rates
  - weekly outreach targets needed to hit a monthly revenue goal
  - stale leads that need a follow-up
- **`data/example_leads.csv`** — **example data only** (fictional companies) so you can run it immediately. Replace with your own leads.
- **`playbook/`** — concise sales & positioning playbook:
  - [`01-ideal-client-profile.md`](playbook/01-ideal-client-profile.md) — ICP + niche positioning worksheet, offer ladder
  - [`02-outreach-templates.md`](playbook/02-outreach-templates.md) — cold email, LinkedIn, referral ask (with follow-ups)
  - [`03-discovery-call-script.md`](playbook/03-discovery-call-script.md) — 30-minute discovery call script
  - [`04-proposal-template.md`](playbook/04-proposal-template.md) — 1-page proposal with 3 pricing options
  - [`05-4-week-mentoring-plan.md`](playbook/05-4-week-mentoring-plan.md) — 4-week plan from positioning to closing & retention

## Run it (one command)

Requires only Python 3.8+ (standard library, nothing to install):

```bash
python3 pipeline.py
```

Use your own numbers:

```bash
python3 pipeline.py --csv data/example_leads.csv --goal 40000 --avg-project 12000 --close-rate 0.2 --reply-rate 0.08
```

| Option | Meaning | Default |
|---|---|---|
| `--csv` | Path to leads CSV | `data/example_leads.csv` |
| `--goal` | Monthly revenue goal (EUR) | 30000 |
| `--avg-project` | Average project value (EUR) | average of Won deals in CSV |
| `--close-rate` | Share of conversations (replies) that become won deals | 0.25 |
| `--reply-rate` | Share of outreach messages that get a reply | 0.10 |
| `--stale-days` | One stale threshold for all open stages | per stage: Contacted 5d, Call booked 3d, Proposal 4d |
| `--today` | Override today's date (YYYY-MM-DD), useful for reproducible reports | today |

Run the tests: `python3 -m unittest discover -s tests`

### CSV format

```
id,company,contact_role,service,source,stage,lost_at,value_eur,last_contact,next_step
```

- `stage`: one of `Prospect`, `Contacted`, `Call booked`, `Proposal`, `Won`, `Lost`
- `lost_at`: for `Lost` leads, the furthest stage reached before losing (so conversion rates stay honest)
- `last_contact`: `YYYY-MM-DD` (blank for prospects not yet contacted)

### How the weekly targets are calculated

```
deals per month          = ceil(revenue goal / avg project value)
conversations per month  = deals / close rate
outreach per month       = conversations / reply rate
weekly                   = monthly / 4.33
```

## Sample output

`python3 pipeline.py --today 2026-10-05` on the example data:

```
=== Lead pipeline report (2026-10-05, 18 leads from data/example_leads.csv) ===

1) Pipeline snapshot
   Prospect       3 leads       EUR 23,500
   Contacted      4 leads       EUR 33,000
   Call booked    2 leads       EUR 15,000
   Proposal       2 leads       EUR 21,500
   Won            3 leads       EUR 46,500
   Lost           4 leads       EUR 38,500
   Open pipeline value: EUR 93,000

2) Stage conversion rates (leads that reached each stage)
   Prospect     -> Contacted     15/18  =  83.3%
   Contacted    -> Call booked    9/15  =  60.0%
   Call booked  -> Proposal       6/9   =  66.7%
   Proposal     -> Won            3/6   =  50.0%
   Overall Prospect -> Won: 3/18 = 16.7%

3) Weekly targets to hit the revenue goal
   Inputs: goal EUR 30,000/month, avg project EUR 15,500 (avg of Won deals in CSV),
           close rate 25% of conversations, reply rate 10% of outreach
   Per month: 2 deals <- 8 conversations <- 80 outreach messages
   Per week:  0.5 deals <- 2 conversations <- 19 outreach messages (~4/workday)

4) Stale leads needing follow-up
   [L12] Sample Coffee Chain        Contacted    17d since contact (limit 5d)     -> Send case study
   [L09] Placeholder Clinic Group   Proposal     15d since contact (limit 4d)     -> Proposal sent - no reply
   [L03] Demo Fitness Studio        Contacted    13d since contact (limit 5d)     -> Send follow-up #2
   [L11] Example Accounting Firm    Call booked  10d since contact (limit 3d)     -> Call was no-show - reschedule
   [L02] Sample Logistics SRL       Proposal     7d since contact (limit 4d)      -> Chase proposal decision
   [L16] Example Car Rental         Contacted    6d since contact (limit 5d)      -> Follow-up scheduled

   6 lead(s) flagged. Thresholds: Contacted 5d, Call booked 3d, Proposal 4d
```

**Reading it:** the weakest stage here is *Proposal → Won* and two proposals have gone quiet — so the first fix is proposal follow-up and walking clients through proposals live, not sending more cold messages.

## How I'd help as your mentor

I'm a software engineer and freelancer (SAP BTP + full-stack) who has had to win and run client work myself. As your mentor I would:

1. **Week 1 — Positioning & offer:** pick a niche from your best past projects, write a positioning statement and an offer ladder (paid audit → core project → retainer), and set your numbers in this tool.
2. **Week 2 — Portfolio & case studies:** turn past projects into results-driven case studies and align your website, Clutch, Upwork and LinkedIn around one message.
3. **Week 3 — Outbound system:** build a target account list and a weekly cadence across LinkedIn, cold email, Upwork, Clutch and referrals, sized by the weekly targets above.
4. **Week 4 — Sales calls, pricing & retention:** role-play discovery calls, move to value-based 3-option proposals, and set up retainers and referral moments.

Between sessions I review your real messages, proposals and pipeline CSV asynchronously and give concrete edits — the goal is a system you run every week on your own, not a one-off push.

---
*All company names and figures in this repository are fictional example data.*
