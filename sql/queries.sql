-- =====================================================================
-- Medicaid Access Monitor - SQL query pack (DuckDB)
-- Tables (created by python/run_sql.py from the clean CSVs):
--   cc      = data/clean/call_center_monthly.csv  (one row per state per month)
--   enr     = data/clean/enrollment_monthly.csv   (one row per state per month)
--   states  = data/lookup/lookup_states.csv       (region, peer group)
-- "Weighted" = busier state-months count more: SUM(wait x calls) / SUM(calls).
-- South Dakota has no call center (blank values), so it drops out of
-- every weighted figure automatically.
-- Each query starts with a line "-- Q##: title" so the runner can split them.
-- =====================================================================

-- Q01: Control totals (must match Python and the Excel Reconciliation tab)
SELECT
    COUNT(*)                                   AS state_months,
    SUM(call_volume)                           AS total_calls,
    COUNT(call_volume)                         AS months_with_volume,
    COUNT(avg_wait_min)                        AS months_with_wait,
    ROUND(SUM(ROUND(call_volume * abandon_rate)))  AS abandoned_calls
FROM cc;

-- Q02: National weighted wait and abandonment by month (charter question 1)
SELECT
    report_month,
    SUM(call_volume)                                                        AS calls,
    ROUND(SUM(call_volume * avg_wait_min) / SUM(call_volume), 1)            AS weighted_wait_min,
    ROUND(100 * SUM(call_volume * abandon_rate) / SUM(call_volume), 1)      AS weighted_abandon_pct
FROM cc
WHERE call_volume IS NOT NULL
GROUP BY report_month
ORDER BY report_month;

-- Q03: Top 10 states by weighted wait over all 17 months (charter question 2)
SELECT
    state_code,
    state_name,
    SUM(call_volume)                                                        AS total_calls,
    ROUND(SUM(call_volume * avg_wait_min) / SUM(call_volume), 1)            AS weighted_wait_min
FROM cc
WHERE call_volume IS NOT NULL
GROUP BY state_code, state_name
ORDER BY weighted_wait_min DESC
LIMIT 10;

-- Q04: Top 10 states by weighted abandonment rate (charter question 2)
SELECT
    state_code,
    state_name,
    SUM(call_volume)                                                        AS total_calls,
    ROUND(100 * SUM(call_volume * abandon_rate) / SUM(call_volume), 1)      AS weighted_abandon_pct
FROM cc
WHERE call_volume IS NOT NULL
GROUP BY state_code, state_name
ORDER BY weighted_abandon_pct DESC
LIMIT 10;

-- Q05: Consistently bad or one bad month? Months with wait over 15 minutes (charter question 2)
SELECT
    state_code,
    COUNT(*) FILTER (WHERE avg_wait_min > 15)      AS months_over_15_min,
    COUNT(avg_wait_min)                            AS months_reported,
    MAX(avg_wait_min)                              AS peak_wait_min
FROM cc
GROUP BY state_code
HAVING COUNT(*) FILTER (WHERE avg_wait_min > 15) > 0
ORDER BY months_over_15_min DESC, peak_wait_min DESC
LIMIT 15;

-- Q06: Florida vs national vs large-state peers, month by month (charter question 3)
SELECT
    c.report_month,
    MAX(CASE WHEN c.state_code = 'FL' THEN c.avg_wait_min END)                                   AS fl_wait,
    ROUND(SUM(c.call_volume * c.avg_wait_min) / SUM(c.call_volume), 1)                            AS national_wait,
    ROUND(SUM(CASE WHEN s.peer_group = 'Large' AND c.state_code <> 'FL' THEN c.call_volume * c.avg_wait_min END)
        / SUM(CASE WHEN s.peer_group = 'Large' AND c.state_code <> 'FL' THEN c.call_volume END), 1)  AS peers_wait,
    ROUND(100 * MAX(CASE WHEN c.state_code = 'FL' THEN c.abandon_rate END), 1)                   AS fl_abandon_pct,
    ROUND(100 * SUM(c.call_volume * c.abandon_rate) / SUM(c.call_volume), 1)                      AS national_abandon_pct
FROM cc c
JOIN states s USING (state_code)
WHERE c.call_volume IS NOT NULL
GROUP BY c.report_month
ORDER BY c.report_month;

-- Q07: Florida's rank among all reporting states each month (window function RANK)
WITH ranked AS (
    SELECT
        report_month,
        state_code,
        avg_wait_min,
        RANK() OVER (PARTITION BY report_month ORDER BY avg_wait_min DESC) AS wait_rank,
        COUNT(*) OVER (PARTITION BY report_month)                          AS states_reporting
    FROM cc
    WHERE avg_wait_min IS NOT NULL
)
SELECT report_month, avg_wait_min AS fl_wait_min, wait_rank AS fl_rank_worst_first, states_reporting
FROM ranked
WHERE state_code = 'FL'
ORDER BY report_month;

-- Q08: Did call volume rise with renewals? National monthly correlation (charter question 4)
WITH monthly AS (
    SELECT c.report_month, SUM(c.call_volume) AS calls, SUM(e.renewals_due) AS renewals_due
    FROM cc c
    JOIN enr e USING (state_code, report_month)
    WHERE c.call_volume IS NOT NULL AND e.renewals_due IS NOT NULL
    GROUP BY c.report_month
)
SELECT
    COUNT(*)                                   AS months_used,
    ROUND(CORR(calls, renewals_due), 2)        AS correlation_calls_vs_renewals
FROM monthly;

-- Q09: Worse phone access vs more paperwork terminations? State-level correlation (charter question 5)
WITH by_state AS (
    SELECT
        c.state_code,
        SUM(c.call_volume * c.abandon_rate) / SUM(c.call_volume)        AS weighted_abandon,
        SUM(e.terminated_procedural) / SUM(e.renewals_due)              AS procedural_share
    FROM cc c
    JOIN enr e USING (state_code, report_month)
    WHERE c.call_volume IS NOT NULL
      AND e.renewals_due IS NOT NULL AND e.terminated_procedural IS NOT NULL
    GROUP BY c.state_code
)
SELECT
    COUNT(*)                                            AS states_used,
    ROUND(CORR(weighted_abandon, procedural_share), 2)  AS correlation_abandon_vs_procedural
FROM by_state;

-- Q10: Most improved: peak monthly wait vs average of the last 3 months (charter question 6)
WITH last3 AS (
    SELECT state_code, AVG(avg_wait_min) AS last3_avg_wait
    FROM cc
    WHERE report_month >= DATE '2024-05-01'
    GROUP BY state_code
)
SELECT
    c.state_code,
    MAX(c.avg_wait_min)                              AS peak_wait_min,
    ROUND(l.last3_avg_wait, 1)                       AS last3_avg_wait_min,
    ROUND(MAX(c.avg_wait_min) - l.last3_avg_wait, 1) AS minutes_improved
FROM cc c
JOIN last3 l USING (state_code)
WHERE c.avg_wait_min IS NOT NULL
GROUP BY c.state_code, l.last3_avg_wait
ORDER BY minutes_improved DESC
LIMIT 10;

-- Q11: Calls per 1,000 enrollees (fair size comparison), top 10
SELECT
    c.state_code,
    SUM(c.call_volume)                                              AS total_calls,
    ROUND(AVG(e.total_enrollment))                                  AS avg_enrollment,
    ROUND(1000.0 * SUM(c.call_volume) / SUM(e.total_enrollment), 1) AS calls_per_1000_enrollee_months
FROM cc c
JOIN enr e USING (state_code, report_month)
WHERE c.call_volume IS NOT NULL
GROUP BY c.state_code
ORDER BY calls_per_1000_enrollee_months DESC
LIMIT 10;

-- Q12: Biggest month-over-month swings in call volume (window function LAG)
WITH m AS (
    SELECT
        state_code,
        report_month,
        call_volume,
        LAG(call_volume) OVER (PARTITION BY state_code ORDER BY report_month) AS prev_volume
    FROM cc
)
SELECT
    state_code,
    report_month,
    prev_volume,
    call_volume,
    ROUND(100.0 * (call_volume - prev_volume) / prev_volume, 0) AS pct_change
FROM m
WHERE prev_volume > 0 AND call_volume IS NOT NULL
ORDER BY ABS((call_volume - prev_volume) / prev_volume) DESC
LIMIT 10;

-- Q13: Region summary
SELECT
    s.region,
    COUNT(DISTINCT c.state_code)                                            AS states,
    SUM(c.call_volume)                                                      AS total_calls,
    ROUND(SUM(c.call_volume * c.avg_wait_min) / SUM(c.call_volume), 1)      AS weighted_wait_min,
    ROUND(100 * SUM(c.call_volume * c.abandon_rate) / SUM(c.call_volume), 1) AS weighted_abandon_pct
FROM cc c
JOIN states s USING (state_code)
WHERE c.call_volume IS NOT NULL
GROUP BY s.region
ORDER BY weighted_wait_min DESC;

-- Q14: Data quality: states with missing or zero-minute months
SELECT
    state_code,
    COUNT(*) FILTER (WHERE call_volume IS NULL)  AS months_missing_volume,
    COUNT(*) FILTER (WHERE avg_wait_min IS NULL) AS months_missing_wait,
    COUNT(*) FILTER (WHERE avg_wait_min = 0)     AS months_zero_wait
FROM cc
GROUP BY state_code
HAVING COUNT(*) FILTER (WHERE call_volume IS NULL) > 0
    OR COUNT(*) FILTER (WHERE avg_wait_min IS NULL) > 0
    OR COUNT(*) FILTER (WHERE avg_wait_min = 0) > 0
ORDER BY months_missing_volume DESC, months_zero_wait DESC;

-- Q15: Each state's single worst month (window function ROW_NUMBER), top 10
WITH ranked AS (
    SELECT
        state_code,
        report_month,
        avg_wait_min,
        abandon_rate,
        ROW_NUMBER() OVER (PARTITION BY state_code ORDER BY avg_wait_min DESC, report_month) AS rn
    FROM cc
    WHERE avg_wait_min IS NOT NULL
)
SELECT state_code, report_month AS worst_month, avg_wait_min AS worst_wait_min,
       ROUND(100 * abandon_rate, 1) AS abandon_pct_that_month
FROM ranked
WHERE rn = 1
ORDER BY worst_wait_min DESC
LIMIT 10;
