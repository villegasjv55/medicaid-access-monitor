# Data Dictionary

Raw column names below are copied exactly from the files downloaded on 2026-11-07. CMS can rename columns between releases, so check again whenever a file is replaced.

**Simple words:** the raw files use CMS's names and layouts. The cleaning script (Phase 2) turns them into two tidy tables with short standard names. This page is the map between the two.

---

## Raw file 1: CAA Reporting Metrics (long format)

| Raw column | What it holds | Example | Notes |
|---|---|---|---|
| `State` | Two-letter state code, or `USA` for national totals | `FL` | `USA` rows have renewal metrics only |
| `Reporting period` | Month the data describes, as YYYYMM | `202307` | Text, not a date |
| `Release date` | Month CMS published that row, as YYYYMM | `202310` | Shows which release each number came from |
| `Metric name ` | Which measure the row holds (19 different ones) | `Average call center wait time (minutes)` | **Trailing space in the header** |
| `Value ` | The number for that metric | `29` | **Trailing space in the header.** Stored as text, and blank when not reported |
| `Data notes` | CMS caveat codes for that value, comma-separated | `C3, C5` | Codes only. See the codes table below |

**"Long" means** each number has its own row. One state-month has 19 rows, one per metric. The cleaning script has to **pivot** (turn rows into columns) so that each state-month becomes a single row.

## Raw file 2: Performance Indicator dataset (wide format; only the columns this project uses)

| Raw column | What it holds | Example | Notes |
|---|---|---|---|
| `State Abbreviation` | Two-letter state code | `FL` | |
| `State Name` | Full state name | `Florida` | Used to add names to the CAA data |
| `Reporting Period` | Month, as YYYYMM | `202307` | |
| `Preliminary or Updated` | `P` = first version, `U` = revised version | `U` | **Every month appears twice. Keep `U` only** |
| `Final Report` | `Y` on Updated rows, `N` on Preliminary rows | `Y` | Matches the column above |
| `Total Medicaid and CHIP Enrollment` | People enrolled at the end of the month | `4632565` | |
| `New Applications Submitted to Medicaid and CHIP Agencies` | New applications received | | Each column has a matching `- footnotes` column |
| `Total Call Center Volume (Number of Calls)` | Same measure as in CAA | `2531455` | Reconciliation only |
| `Average Call Center Wait Time (Minutes)` | Same measure as in CAA | `41` | Reconciliation only |
| `Average Call Center Abandonment Rate` | Same measure as in CAA | `0.43` | Reconciliation only |

The other 34 PI columns (determination counts, processing-time buckets, child/adult enrollment, and footnotes) are out of scope for now.

---

## Clean table 1: `call_center_monthly`
One row per state per month: 51 states × 17 months = **867 rows**.

| Standard name | Comes from | Type | Meaning (simple words) | Example | Known issues |
|---|---|---|---|---|---|
| `state_code` | CAA `State` | text | Two-letter state code | `FL` | Drop `USA` (no call-center data) |
| `state_name` | PI `State Name` (lookup) | text | Full state name | `Florida` | Not in the CAA file |
| `report_month` | CAA `Reporting period` | date | First day of the month | `2023-07-01` | Convert from `202307` |
| `call_volume` | CAA `Value ` where metric = `Total call center volume (number of calls)` | integer | Calls received by all Medicaid/CHIP call centers in the state | `2531455` | States define "call center" differently |
| `avg_wait_min` | CAA `Value ` where metric = `Average call center wait time (minutes)` | number | Average minutes on hold before reaching an agent | `41` | Whole minutes only. **79 state-months show 0** (under about 30 seconds rounds to 0) |
| `abandon_rate` | CAA `Value ` where metric = `Average call center abandonment rate` | number 0–1 | Share of callers who hung up before being answered | `0.43` (= 43%) | Already a decimal, so no "%" conversion is needed |
| `is_reported` | created | true/false | False when the value is blank or the state has no call center | `true` | False for SD (all 17 months) and NV volume/abandonment for Nov 2023 |
| `data_note` | CAA `Data notes` | text | CMS caveat codes | `C3, C5` | One set of codes per metric. Keep all three, joined |
| `release_month` | CAA `Release date` | date | When CMS published the row | `2023-10-01` | |
| `source_file` | created | text | Raw file name | `medicaid-chip-caa-…-october-2024-release.csv` | |

## Clean table 2: `enrollment_monthly`
One row per state per month for the same 17 months.

| Standard name | Comes from | Type | Meaning (simple words) | Example | Known issues |
|---|---|---|---|---|---|
| `state_code` | both files | text | Two-letter state code | `FL` | |
| `report_month` | both files | date | First day of the month | `2023-07-01` | |
| `total_enrollment` | PI `Total Medicaid and CHIP Enrollment` (U rows) | integer | People enrolled in Medicaid + CHIP | `4632565` | Used for "calls per 1,000 enrollees" |
| `applications_received` | PI `New Applications Submitted to Medicaid and CHIP Agencies` (U rows) | integer | New applications that month | | |
| `renewals_due` | CAA metric `Total number of beneficiaries due for renewal in the reporting month (Metric 5)` | integer | People whose renewal was due that month | | |
| `terminated_procedural` | CAA metric `Total beneficiaries whose coverage was terminated for a procedural or administrative reason (Metric 5c)` | integer | People removed for paperwork reasons, not because they were found ineligible | `81883` (FL, Jul 2023) | Blank for some state-months (e.g. FL Mar 2023) |
| `source_file` | created | text | Raw file(s) used | | |

---

## CMS data-note codes (call-center metrics)

| Code | Meaning | Confirmed by |
|---|---|---|
| C3 | Does not include all calls received by call centers | Georgetown CCF analysis of CMS notes |
| C4 | Does not include all calls received after business hours | Georgetown CCF analysis of CMS notes |
| C6 | Includes only calls transferred to a live agent | Georgetown CCF analysis of CMS notes |
| C10 | Appears on all of South Dakota's blank rows (SD has no call center) | Pattern in the file |
| C1, C2, C5, C7, C8, C9, C11, C12, C13 | _To confirm from the CMS data notes in the monthly Excel releases_ | — |

How often codes appear on call-center rows: C4 1,597 · C6 1,341 · C5 1,332 · C3 872 · C2 527 · C7 357 · C1 351 · C10 51 · C9 34 · C13 17 · C8 15 · C11 2 · C12 2.

---

## Known issues found in the real files (these go into the exceptions log in Phase 2)

1. **South Dakota has no call-center data.** All 51 SD call-center values (17 months × 3 metrics) are blank, with note C10. Mark `is_reported = false` and exclude SD from rankings.
2. **Nevada, November 2023:** call volume and abandonment rate are blank (note C12), but wait time = 38 is reported. Keep the wait time and flag the month.
3. **Rhode Island volume drops by about 86% between April and May 2023** (61,842 → 8,530 calls). That points to a change in what was counted, not a real drop in callers. The project guide mentions a Rhode Island method change in November 2023. **Check the RI notes before choosing which date to treat as the method change.**
4. **79 state-months report a 0-minute wait.** NC has 15, MS 12 and IA 9. Under about 30 seconds rounds to 0, so 0 means "very short," not "no wait."
5. **The PI file was revised after the CAA release.** 22 volume, 29 wait and 38 abandonment values differ, mostly Nebraska (Mar–Jul 2023 volume) and Hawaii. CAA stays the main source, and the differences go on the reconciliation tab.
6. **PI rows come in pairs** (Preliminary and Updated). Keep `U` only, or every enrollment number gets counted twice.
7. **The two CAA headers have trailing spaces** (`Metric name `, `Value `). Strip them in the script.
