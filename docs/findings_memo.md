# MEMO

**To:** Director, Medicaid Contact Center Operations (Florida)
**From:** Juan Villegas, Villegas Analytics
**Date:** November 12, 2026
**Re:** Call-center access during Medicaid unwinding: findings and recommendations

---

## Bottom line

During unwinding (March 2023 – July 2024), Florida's Medicaid call center was **one of the hardest in the country to reach.** Callers waited **about 31 minutes** on average, which is **twice the national average and five times the other large states.** **37% hung up** before reaching anyone: about **13.4 million calls**. Florida ranked **3rd worst of 50 reporting states**, and its wait was over 15 minutes in **all 17 months**. Access improved in 2024, but not enough to close the gap. The fix is to staff to the renewal calendar, cut avoidable calls, and manage the queue with weekly targets.

## What the data shows

| Measure (Mar 2023 – Jul 2024) | Florida | National | Large-state peers (TX, CA, NY, GA, PA) |
|---|---|---|---|
| Weighted average wait | **30.8 min** | 14.4 min | 6.3 min |
| Callers who hung up | **37.4%** | 18.4% | 10.7% |
| Total calls | 35.8 million (23% of U.S.) | 154.7 million | 41.6 million |
| Months with wait over 15 minutes | **17 of 17** | — | — |
| Rank (1 = worst access, risk score) | **3 of 50** | — | — |

1. **The problem was constant, not a one-month spike.** Florida ranked between 2nd and 8th worst every month. Its worst months were November 2023 (42 minutes, 44% hung up), July 2023 (41 minutes, 43%) and April 2023 (40 minutes, 50%).
2. **Florida carried the heaviest call load in the country:** 487 calls per 1,000 enrollees per month, against 314 for the next-highest state (Utah). Volume peaked at **2.6 million calls in January 2024**.
3. **Calls followed renewals.** Nationally, monthly call volume and renewals due moved together (correlation 0.94). Peaks were predictable from the renewal calendar.
4. **Some improvement in 2024.** Florida's weighted wait fell from 34.1 minutes (2023) to 26.7 minutes (Jan–Jul 2024), and hang-ups fell from 39.2% to 35.1%. It was still about twice the national level (12.6 minutes in 2024).
5. **Other states show recovery is possible.** Maine went from a 44-minute peak to under 6 minutes, Oklahoma from 46 to under 10, and Idaho from 56 to under 19.
6. **Context:** Florida's enrollment fell from 5.09 million to 3.80 million over the period. Procedural (paperwork-related) terminations were about 22% of renewals due in Florida. Across states, phone access and procedural terminations were only weakly related (correlation 0.13), so long waits alone do not explain terminations.

## Recommendations

1. **Staff to the renewal calendar.** Calls track renewals almost one-to-one, so forecast weekly call volume from the number of renewals due and schedule agents 4–6 weeks ahead of each renewal wave. Add temporary or vendor capacity for the peak months.
2. **Cut avoidable calls.** Expand automatic (ex parte) renewals, send plain-language renewal notices with clear deadlines, and add self-service status checks (web, text and IVR) so people don't need an agent to ask "did you get my paperwork?"
3. **Stop losing callers in the queue.** Offer a scheduled or virtual callback once the wait passes 10 minutes, and publish an expected-wait message at the start of the call.
4. **Manage to weekly targets.** Track average wait, abandonment rate and calls per 1,000 enrollees every week, with clear thresholds (for example, wait under 15 minutes and abandonment under 15%) and a named owner for each.
5. **Learn from recovered states.** Contact Maine, Oklahoma and Idaho to find out which changes cut their waits so quickly.

## Limits of this analysis

- States define "call center" differently, so comparisons show broad patterns, not exact rankings.
- Wait times are whole-minute monthly averages and hide the range of individual waits.
- South Dakota has no call center and is excluded; some states changed how they counted calls (Rhode Island, Hawaii, Arizona).
- These findings describe patterns, not causes.

**Data and method:** CMS Medicaid and CHIP CAA Reporting Metrics (October 2024 release) and the Performance Indicator dataset (March 2026 release). Totals reconcile across Python, SQL and Excel (867 state-months, 154,681,330 calls, 28,472,216 abandoned calls). Live dashboard: https://medicaid-access-monitor.streamlit.app/
