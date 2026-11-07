# Data Sources Log

Rule: files in `data/raw/` are never edited. If a source is downloaded again, add a new row and keep the old file.

## Raw files

| # | File name (in `data/raw/`) | Dataset | Publisher | Download date | Date range covered | Rows × columns | Format |
|---|---|---|---|---|---|---|---|
| 1 | `medicaid-chip-caa-reporting-metrics-long-table-october-2024-release.csv` | Medicaid and CHIP CAA Reporting Metrics (October 2024 release) | CMS, via download.medicaid.gov / data.medicaid.gov | 2026-11-07 | March 2023 – July 2024 (17 reporting months) | 16,745 × 6 | Long table: one row per state, month and metric |
| 2 | `pi-dataset-march-2026release.csv` | State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data (Performance Indicator dataset, March 2026 release) | CMS, via download.medicaid.gov / data.medicaid.gov | 2026-11-07 | September 2013 – December 2025 | 10,506 × 44 | Wide table: one row per state, month and version (Preliminary / Updated) |

**Download links**
1. https://download.medicaid.gov/data/medicaid-chip-caa-reporting-metrics-long-table-october-2024-release.csv
2. https://download.medicaid.gov/data/pi-dataset-march-2026release.csv

## What each file is used for

| File | Role in this project |
|---|---|
| CAA Reporting Metrics | **Main source.** Call-center volume, wait time and abandonment rate, plus renewals due and procedural terminations, for every state during unwinding. This is the dataset CMS published as the official unwinding record. |
| Performance Indicator (PI) dataset | **Context and reconciliation.** Total enrollment and new applications (to compare states by size), and a second, later-revised copy of the same call-center numbers. Comparing the two is my reconciliation check. |

## Facts recorded from the files (checked 2026-11-07)

**CAA file**
- 17 reporting months: 202303 to 202407. CMS published the March and April 2023 months together in the July 2023 release.
- "Release date" values run from 202307 to 202410. Each month's row carries the release in which it was published.
- 52 state codes: the 50 states, DC, and `USA` (national totals). **`USA` rows have renewal metrics only, with no call-center metrics.**
- 19 different metrics: 16 renewal metrics (Metrics 4–5d and their percentages) and 3 call-center metrics.
- Call-center rows: 867 (51 states × 17 months). 850 have values. 17 are blank for South Dakota (no call center) and 2 are blank for Nevada in November 2023.
- No duplicate state + month + metric rows.
- The column headers `Metric name ` and `Value ` end with a trailing space.

**PI file**
- 51 state codes (50 states + DC) and no national row.
- Every state-month appears twice: once as **P** (Preliminary, `Final Report = N`) and once as **U** (Updated, `Final Report = Y`). That's 5,253 of each.
- Call-center columns are empty for most months before the unwinding period.

## Reconciliation preview (CAA vs PI Updated, call-center metrics)
Most of the 850 reported state-months match exactly. Some do not:

| Metric | Mismatched state-months | Examples |
|---|---|---|
| Call volume | 22 | NE Mar–Jul 2023 (44,710 in CAA vs 31,697 in PI for Mar 2023); HI Nov 2023; KY Jul 2023 off by 1 |
| Wait time | 29 | HI several months (e.g. Jan 2024: 31 vs 7 min) |
| Abandonment rate | 38 | HI several months |
| Present in CAA, blank in PI | 1 | AZ Oct 2023 |

**Decision:** use the CAA file as the main source, because it is the official unwinding record and is fixed in time. The PI differences are later state revisions. They will be logged in the exceptions log and shown on the Excel reconciliation tab.

## Reference files (for reconciliation, optional)
| File name (in `docs/reference/`) | What it is | Month(s) shown | Download date |
|---|---|---|---|
| _optional_ | CMS Unwinding Operations Snapshot (PDF) | | |
