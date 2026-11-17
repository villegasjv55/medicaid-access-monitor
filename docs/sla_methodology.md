# SLA Compliance Methodology

**Module:** CX & SLA Compliance (added Nov 2026)
**Question it answers:** Did each state's Medicaid call center meet a basic service standard each month, how often, and who keeps missing it?

## The standards

| SLA | Standard | Why this number |
|---|---|---|
| Wait-time SLA | Average wait <= 10 minutes | Sits between the large-state peer average (6.3 min) and the national average (14.4 min) found earlier in this project |
| Abandonment SLA | Abandon rate <= 5% | A common call-center service target |
| Overall SLA | Both met in the same month | One pass/fail flag per state-month |
| Watch list | 3+ months in a row missed | Separates one bad month from a pattern that needs follow-up |

**Honesty note:** these are analyst-defined, illustrative standards. They are **not** official CMS rules. They live in `config/sla_config.json`, so anyone can change a number and re-run `python python/run_pipeline.py` to see the new results.

## How a state-month is scored

- **Evaluated** only when both average wait and abandonment rate are reported. Missing months are not counted as passes or misses. South Dakota has no call-center data, so it is not scored.
- **Compliance %** = months that met the SLA / months evaluated.
- **Miss streak** = the longest run of back-to-back evaluated months that missed. A month with missing data breaks a streak. It's calculated in SQL with the "gaps and islands" method (two ROW_NUMBER windows).

## Where it lives

| Piece | File |
|---|---|
| Standards | `config/sla_config.json` |
| SLA queries | `sql/queries.sql`, Q16 (flags per state-month), Q17 (by state), Q18 (by month), Q19 (miss streaks) |
| One-command refresh | `python/run_pipeline.py` |
| Daily KPI report | `output/kpi_report_YYYY-MM-DD.csv` and `output/sla_summary.md` |
| Run history | `logs/pipeline_log.txt` |

## Checks (run every time)

The pipeline stops and shows FAIL unless all 10 checks pass. They include: Python and SQL agree on state-months and total calls, Python recalculates the SLA flags on its own and gets the same count as SQL, the by-state and by-month totals add back up to the state-month table, all percentages are between 0 and 100, and the KPI report has exactly one row per state.

## Results (first run, Nov 17 2026)

- 849 state-months evaluated (50 states x 17 months, minus Nevada Nov 2023, which is missing data).
- Overall SLA compliance: **33.6%**. Wait SLA: 64.7%. Abandonment SLA: 34.7%. Abandonment is the bigger problem.
- Compliance by month fell from 42% of states (Mar 2023) to 38% (Jul 2024), during the Medicaid renewal period.
- **43 states** missed 3+ months in a row at some point.
- **Florida met the SLA in 0 of 17 months**, the longest possible miss streak.

## Limits

- The data reports monthly averages, so a state can pass on average and still have bad days.
- Different states measure "wait" slightly differently (see the data notes in `data/clean/call_center_monthly.csv`).
- A stricter or looser standard changes the ranking, which is why the thresholds are a config setting and not hard-coded.
