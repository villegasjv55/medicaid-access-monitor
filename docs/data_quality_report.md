# Data Quality Report

**Project:** Medicaid Access Monitor · **Script:** `python/clean_data.py` · **Run date:** November 7, 2026
**Inputs:** CMS CAA Reporting Metrics (October 2024 release) and the Performance Indicator dataset (March 2026 release). See `data_sources.md`.

**Simple words:** before any analysis, every number was checked. Nothing was deleted or changed quietly. Every problem is listed in `data/clean/exceptions_log.csv` with what was found and what was done.

---

## 1. Results at a glance

| Item | Result |
|---|---|
| Raw call-center rows read | 2,601 (867 state-months × 3 metrics) |
| Clean state-months produced | 867 (51 states × 17 months) |
| Rows excluded | 0 |
| **Row-count check** | ✅ 2,601 in = 2,601 kept + 0 excluded |
| **Control total (call volume)** | ✅ 154,681,330 calls in raw = 154,681,330 in clean |
| Fully reported state-months | 849 of 867 (all three call-center metrics present) |
| Exceptions logged | 417 |
| CAA vs PI differences | 89 |
| Re-run test | ✅ Running the script twice gives identical files |

## 2. Every check, what it found, and what I did

| # | Check | Rule | Found | Action |
|---|---|---|---|---|
| 1 | Valid state | State code in the 50 states + DC | 0 problems (the `USA` national rows have no call-center data, so they never enter the table) | — |
| 2 | Date range | Month between Mar 2023 and Jul 2024 | 0 problems | — |
| 3 | Duplicates | One value per state + month + metric | 0 duplicates | — |
| 4 | Missing call-center values | Blank, "NR" or "-" | 53 values: South Dakota, all 17 months × 3 metrics (51); Nevada, Nov 2023 call volume and abandonment rate (2) | Kept as blank, `is_reported = False`, left out of KPIs. **Never filled in with a guess.** |
| 5 | Missing renewal data | Blank renewals due / procedural terminations | 95 state-months each: 47 in Mar 2023, 33 in Apr 2023, 14 in May 2023, 1 in Jun 2023 | Kept as blank. These are mostly states that had not started unwinding renewals yet. The renewal KPIs use only months with data. |
| 6 | Missing enrollment data | Blank enrollment / applications | 0 | — |
| 7 | Ranges | Volume ≥ 0; wait 0–180 min; abandonment 0–1 | 0 out of range (wait max 72 min; abandonment max 0.652) | — |
| 8 | Zero waits | Average wait = 0 minutes | 79 state-months in 15 states (most: NC 15, MS 12, IA 9) | Kept. CMS reports whole minutes, so 0 means "under about 30 seconds," not "no wait." |
| 9 | Big jumps | Call volume up more than 200%, or down to less than a third, in one month | 6: AZ Sep 2023 (−69%) and Oct 2023 (−67%); HI Aug 2023 (+254%), Nov 2023 (−82%) and Dec 2023 (+390%); RI May 2023 (−86%) | Flagged for review and not changed. These look like reporting changes, not real swings in callers. |
| 10 | Row counts | Rows in = rows out + rows excluded | Match | Script stops if not |
| 11 | Control total | Raw call volume = clean + excluded | Match | Script stops if not |
| 12 | Reconciliation | CAA value = PI (Updated) value | 89 differences (22 volume, 29 wait, 38 abandonment) | Kept the CAA value. Every difference is listed in `reconciliation_caa_vs_pi.csv`. |

## 3. Reconciliation: CAA vs PI

CMS published the call-center numbers twice: once in the CAA release (the official unwinding record) and again in the PI dataset, which states kept revising afterwards. Most of the 850 reported state-months match exactly. The 89 differences are concentrated in a few states:

| State | Volume | Wait | Abandonment | Comment |
|---|---|---|---|---|
| Nebraska | 17 | 11 | 17 | Most differences. PI volume is about 30–35% lower in Mar–Jul 2023, which suggests a later change in which calls were counted |
| Hawaii | 1 | 9 | 11 | Matches the big jumps flagged in check 9 |
| New Hampshire | 2 | 2 | 2 | |
| Arizona | 1 | 1 | 1 | Oct 2023 is in CAA but blank in PI |
| Others (DC, ID, KS, KY, ME, NV, TX, WA) | 1 | 6 | 7 | Small corrections, e.g. KY Jul 2023 volume off by 1 call |

**Decision:** the analysis uses CAA values throughout. If a Nebraska or Hawaii result looks important later, I'll show it with the PI value next to it.

## 4. Limits that stay true after cleaning

1. **States define "call center" differently.** Some count every hotline, others only one, and some include calls about SNAP or the state marketplace. Comparisons between states show broad patterns, not exact rankings.
2. **CMS caveat codes are on almost every value** (for example C3 "does not include all calls," C4 "does not include after-hours calls," C6 "only calls transferred to a live agent"). These are kept in the `data_note` column so they travel with each number.
3. **Wait time is in whole minutes,** so small differences between fast states are invisible.
4. **Averages hide the range.** A 10-minute average can include many 1-minute calls and some 60-minute calls.
5. **The same metric can mean different things for different states** because of reporting changes (RI, HI, AZ), so trends for those states need a footnote.
6. **No causal claims.** This data can show that long waits and procedural terminations happened together, not that one caused the other.

## 5. Output files

| File | Rows | What it is |
|---|---|---|
| `data/clean/call_center_monthly.csv` | 867 | One row per state per month: volume, wait, abandonment, `is_reported`, CMS notes |
| `data/clean/enrollment_monthly.csv` | 867 | Enrollment, applications, renewals due, procedural terminations |
| `data/clean/exceptions_log.csv` | 417 | Every flagged or missing value and the action taken |
| `data/clean/reconciliation_caa_vs_pi.csv` | 89 | Every value where CMS's two copies disagree |
