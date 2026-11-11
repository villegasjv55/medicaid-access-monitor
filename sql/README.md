# SQL Query Pack (DuckDB)

15 documented queries that answer the 6 questions in the project charter, using the clean tables from `python/clean_data.py`.

**How to run** (from the project folder):

    python python/run_sql.py

The runner loads the clean CSVs into an in-memory DuckDB database, runs every query in `queries.sql`, prints the results, and saves each one to `sql/results/Q##.csv`.

## Queries

| # | Question | SQL skills shown |
|---|---|---|
| Q01 | Control totals: do they match Python and Excel? | COUNT, SUM |
| Q02 | National weighted wait and abandonment by month | GROUP BY, weighted average |
| Q03 | Top 10 states by weighted wait | GROUP BY, ORDER BY, LIMIT |
| Q04 | Top 10 states by weighted abandonment | GROUP BY, ORDER BY, LIMIT |
| Q05 | Consistently bad, or one bad month? | COUNT ... FILTER, HAVING |
| Q06 | Florida vs national vs large-state peers by month | JOIN, CASE WHEN |
| Q07 | Florida's rank among all states each month | Window function RANK() |
| Q08 | Did call volume rise with renewals? | CTE, CORR |
| Q09 | Worse phone access vs more procedural terminations? | CTE, JOIN, CORR |
| Q10 | Most improved states | CTE, date filter |
| Q11 | Calls per 1,000 enrollees | JOIN, ratio |
| Q12 | Biggest month-over-month swings | Window function LAG() |
| Q13 | Region summary | JOIN to lookup table |
| Q14 | Data quality: missing and zero-minute months | COUNT ... FILTER, HAVING |
| Q15 | Each state's single worst month | Window function ROW_NUMBER() |

## What the queries found

- **Reconciliation:** 867 state-months, 154,681,330 calls and 28,472,216 abandoned calls. These match the Python pipeline and the Excel Reconciliation tab exactly.
- **Worst month nationally:** July 2023, with a 20.2-minute weighted wait and 22.6% of callers hanging up.
- **Florida was bad every month.** Its wait was over 15 minutes in all 17 months, and it ranked between 2nd and 8th worst of 50 reporting states every single month.
- **Florida had the highest call load in the country:** 486.7 calls per 1,000 enrollees per month, against 313.5 for the next state (Utah).
- **Calls followed renewals.** National monthly call volume and renewals due moved together (correlation 0.94).
- **Phone access vs procedural terminations:** weak relationship across states (correlation 0.13). Long waits alone don't explain which states removed more people for paperwork reasons. This is correlation only, not cause.
- **Recovery is possible.** Several states cut waits by 30+ minutes from their peak (Maine 44 → 5.7, Idaho 56 → 18.7, Oklahoma 46 → 9.7).

Notes: "weighted" means busier state-months count more. South Dakota has no call center and drops out of every weighted figure. Correlations describe patterns, not causes.
