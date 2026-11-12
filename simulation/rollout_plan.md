# ⚠️ SIMULATED SCENARIO: Florida Medicaid Call Center Recovery Pilot

> **Everything in this folder is a practice scenario, not real events.** No state ran this pilot. The **baseline** numbers are real (Florida's January–July 2024 averages from CMS data); the **weekly results are invented** to show how I would plan, track and report a rollout. Files: `rollout_tracker.csv` (tasks), `simulated_weekly_kpis.csv` (weekly KPIs).

## Purpose
Show how the recommendations in the [findings memo](../docs/findings_memo.md) could be rolled out over **12 weeks**, tracked with a task plan, and reported to leadership every week.

## Targets

| KPI | Real baseline (FL, Jan–Jul 2024) | 12-week target |
|---|---|---|
| Average wait | 26.7 min | **15 min or less** |
| Callers who hung up | 35.1% | **15% or less** |
| Calls per 1,000 enrollees (weekly) | ~112 | Down about 15% through self-service |

## Workstreams (14 tasks in `rollout_tracker.csv`)

| Workstream | What it does | Owner role |
|---|---|---|
| Governance | Charter, targets, weekly KPI review | Program Manager |
| Forecasting | Predict weekly calls from the renewal calendar | Reporting Analyst |
| Staffing | Schedule agents ahead of renewal waves; overflow vendor | Workforce Manager |
| Queue | Virtual callback after 10 minutes; expected-wait message | Telephony Lead |
| Deflection | Self-service status checks, clearer notices, more automatic renewals | IT Implementation Analyst, Communications, Policy |
| Training | Refresher on the top 10 call reasons | Training Lead |
| Reporting | Weekly dashboard to leadership; close-out lessons | Reporting Analyst |

## Timeline

| Weeks | Focus |
|---|---|
| 1–2 | Kickoff, targets, KPI review set up |
| 3–4 | Forecast built and validated; callback and wait message live |
| 4–7 | Overflow agents onboarded; staffing schedules follow the forecast |
| 4–10 | Self-service status check built and launched |
| 5–12 | Automatic renewals expanded |
| 11–12 | Lessons learned and scale-up recommendation |

## Simulated results at week 12

| KPI | Baseline | Week 12 (simulated) | Target met? |
|---|---|---|---|
| Average wait | 26.7 min | 13.0 min | ✅ (met from week 8) |
| Callers who hung up | 35.1% | 15.5% | ❌ Not yet: just above 15% |
| Calls per 1,000 enrollees (weekly) | 112 | 93 | ✅ About 17% lower |

**Status at week 12 (simulated):** 11 of 14 tasks complete, 3 in progress (staffing schedules, automatic renewals, close-out).

## Risks and responses

| Risk | Impact | Response |
|---|---|---|
| Renewal wave bigger than forecast | Waits jump again | Weekly forecast refresh; vendor overflow on standby |
| Callback queue overloaded | Callers still lost | Cap callbacks per hour; add evening callback shifts |
| Self-service adoption is slow | Call volume stays high | Promote it in notices and the IVR greeting |
| Data definitions change mid-pilot | KPIs not comparable | Freeze definitions in the charter; log any change |

## How this would be reported
Every week: one dashboard page (wait, abandonment, calls per 1,000, tasks on track), a three-line summary for leadership, and a decision list for anything off track. That's the same reporting habit used in the rest of this project.
