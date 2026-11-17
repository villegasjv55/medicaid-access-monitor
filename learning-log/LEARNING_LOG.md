# Learning Log: Medicaid Access Monitor

Written in my own words, at the end of each work session. "Why" matters more than "what."

---

## Day 1 – Setup, data and scope (date: November 7, 2026)

**What I did today**
- Created the project folder, the Python virtual environment and the GitHub repo (villegasjv55/medicaid-access-monitor).
- Downloaded two real CMS files into data/raw/: the CAA Reporting Metrics (call centers during unwinding, Mar 2023 – Jul 2024) and the Performance Indicator dataset (enrollment and applications).
- Wrote the project charter, the data sources log and the data dictionary.

**Decisions I made and why**
- Used the CAA file as the main source because it is CMS's official record of the unwinding period.
- Wrote the data dictionary before any code, so every raw CMS column is mapped to a short standard name and I know exactly where each number comes from.

**Problems I hit and how I solved them**
- Getting files onto my Mac and pushing to GitHub took a few tries. I learned to check with `ls` and `git status` before assuming something worked.
- One dataset link was dead (404). I found the official CMS download link instead.

**Questions I must be able to answer**
1. What is unwinding, in my own words?
2. What are the three call-center metrics, and why is abandonment rate important?
3. Why should I never edit files in data/raw?

**My answers**
1. During COVID, states were not allowed to remove people from Medicaid. When that rule ended in 2023, every state had to re-check everyone's eligibility, which is called "unwinding." Millions of people had to renew, and many called their state's Medicaid call center for help.
2. Call volume (how many people called), average wait time (how long they sat on hold before reaching a person), and abandonment rate (the share of callers who hung up before anyone answered). Abandonment matters because every abandoned call is a person who needed help and didn't get it. During unwinding, that could mean missing a renewal and losing coverage for paperwork reasons.
3. The raw files are my proof of what CMS actually published. If I edit them, I can't show where my numbers came from or redo the cleaning from scratch. All changes happen in the cleaning script, and every change is logged.

---

## Day 2 – Cleaning and data quality (date: November 7, 2026)

**What I did today**
- Built python/clean_data.py. It reads the two raw CMS files, turns the call-center data from "long" (one row per metric) into one row per state per month, and saves two clean tables: call_center_monthly.csv and enrollment_monthly.csv (867 rows each = 51 states x 17 months).
- Added quality checks: valid states, date range, duplicates, missing values, allowed ranges, 0-minute waits, big month-over-month jumps, row counts and control totals.
- Every problem goes into data/clean/exceptions_log.csv (417 rows). Nothing is fixed or deleted quietly.
- Compared CMS's two copies of the call-center numbers (CAA vs PI) and saved the 89 differences to reconciliation_caa_vs_pi.csv.

**Decisions I made and why**
- Kept the CAA file as my main source because it is CMS's official unwinding record and does not change. The PI file was revised later, so I use it only to reconcile.
- Kept only the "Updated" rows from the PI file. Each month appears twice (Preliminary and Updated), and keeping both would count enrollment twice.
- Left blanks as blanks and marked is_reported = False. Filling them in with a guess would make my numbers look more complete than they really are.

**Questions I must be able to answer**
1. Why is "never silently change data" important to an employer?
2. What is a control total, and what did mine prove?
3. Name two real data problems I found and how I handled them.

**My answers**
1. If I change or delete numbers without writing it down, nobody can trust my reports or trace a number back to where it came from. A manager needs to know that what they see is the real data, plus a clear list of anything I flagged. That is why every change goes into the exceptions log with what I found and what I did.
2. A control total is a simple sum I check before and after cleaning to prove nothing was lost or added. Mine was total call volume: 154,681,330 calls in the raw file and 154,681,330 calls in the clean table, with 0 excluded. The row count matched too (2,601 raw rows = 2,601 kept). If either didn't match, the script stops with an error.
3. (a) South Dakota has no call center, so all its call-center values are blank. I kept the rows, marked is_reported = False, and will leave SD out of the rankings instead of treating it as a zero. (b) Rhode Island's call volume dropped 86% in one month (61,842 to 8,530 in May 2023). A drop that big is almost certainly a change in how calls were counted, not fewer people calling, so I flagged it as a "big_jump" for review and did not change the number. Hawaii and Arizona had similar jumps. Also, 79 state-months show a 0-minute wait. CMS rounds anything under about 30 seconds down to 0, so 0 means "very short," not "no waiting."

---

## Day 3 – Excel reporting workbook (dates: November 9–11, 2026)

**What I did**
- Loaded the raw CMS files into Excel with Power Query (Raw_CallCenter, Raw_Enrollment, Lookup_States), using the Advanced Editor with named steps.
- Built Calc_Monthly (joined table + XLOOKUP, abandoned calls, calls per 1,000, month-over-month change), a Reconciliation tab (all PASS), State_Scorecard (weighted KPIs, risk score, rank, color scales, Top 10), Florida_Spotlight, National_Trend (PivotTable with weighted calculated fields, PivotChart, region slicer) and a README tab.

**Decisions I made and why**
- Used weighted averages (wait × calls ÷ calls) so big states and busy months count more. A simple average would let a tiny state count as much as Florida.
- Built the Reconciliation tab early, so every later tab is built on numbers I already proved match Python.
- Left South Dakota out of rankings instead of giving it a "perfect" 0-minute score.

**Problems I hit and how I solved them**
- Clicking the filter arrows crashed Power Query on my Mac, so I pasted the full recipe in the Advanced Editor instead.
- My workbook was saving to the Desktop instead of the project folder. I found it with `mdfind` and moved it.
- A lookup formula grabbed the header row ("state_code") instead of Alaska. A COUNTIF test showed 1 instead of 17, which pointed to the cause.
- The PivotTable showed "Count" (51) instead of "Sum", because some cells are blank text. I changed it to Sum.

**Questions I must be able to answer**
1. What is Power Query and why use it?
2. Why does the PivotTable need a calculated field for the weighted wait?
3. What does the Reconciliation tab prove?

**My answers**
1. Power Query is Excel's tool for importing and cleaning data with recorded steps. The steps can be refreshed with one click when new data arrives, so the report updates without redoing the work by hand.
2. Adding up wait times doesn't make sense, and averaging them treats every state the same. The calculated field divides total "wait × calls" by total calls for each month, which gives the true weighted average.
3. It proves the Excel workbook gives exactly the same totals as my Python pipeline (867 rows, 154,681,330 calls, 28,472,216 abandoned calls), so nothing was lost or changed along the way.

---

## Day 4 – SQL, dashboard and wrap-up (dates: November 11–12, 2026)

**What I did**
- Wrote 15 SQL queries in DuckDB (sql/queries.sql) and a runner (python/run_sql.py) that saves every result. Q01 matches Python and Excel exactly.
- Built a report-style Streamlit dashboard (map, state ranking, Florida spotlight, compare states, filters) and published it live at medicaid-access-monitor.streamlit.app.
- Finished the findings memo, the rollout simulation (clearly labeled), the 7-slide executive briefing and the career kit.

**Decisions I made and why**
- Ran SQL on the clean tables (not the raw files), so all three tools start from the same source of truth.
- Labeled the rollout simulation as SIMULATED everywhere. Only the baseline is real data, so nobody can mistake it for real results.
- Said "patterns, not causes" whenever I mention correlations (calls vs renewals 0.94; access vs terminations 0.13).

**Questions I must be able to answer**
1. What is a window function? Give an example from my project.
2. Why does correlation not mean cause?
3. What would I recommend to Florida, and why?

**My answers**
1. A window function calculates something across related rows without collapsing them into one row. In Q07 I used RANK() OVER (PARTITION BY month ORDER BY wait DESC) to get Florida's rank among all states in every month. In Q12 I used LAG() to compare each month with the month before.
2. Two things can move together because of a third thing, or by coincidence. Calls and renewals rising together makes sense, but the data alone can't prove one caused the other. That's why I describe patterns and keep the claims honest.
3. Staff to the renewal calendar (calls track renewals almost one-to-one), cut avoidable calls with self-service and automatic renewals, add callbacks so people stop hanging up, manage to weekly targets, and learn from states like Maine and Oklahoma that cut their waits fast.

---

## Day 5 – CX & SLA compliance module (date: November 17, 2026)

**What I did**
- Set service standards in a config file (wait ≤ 10 minutes, abandonment ≤ 5%) and wrote 4 new SQL queries: SLA flags per state-month (Q16), compliance by state (Q17), compliance by month (Q18) and miss streaks (Q19).
- Built `python/run_pipeline.py`, one command that cleans the data, runs all 19 queries, applies the standards, writes a dated KPI report and a summary, runs 10 PASS/FAIL checks and logs every run.
- Added an `SLA_Compliance` tab in Excel and 3 new rows on the Reconciliation tab (10 of 10 PASS).
- Built and published a Tableau Public dashboard: KPI strip, map, monthly trend, watch list, region and peer-group filters.

**Decisions I made and why**
- Put the standards in a config file instead of hard-coding them, so a manager can change a target and re-run without touching code.
- Only scored months where both wait and abandonment were reported, so missing data doesn't count as a pass or a miss.
- Added tie-breakers (`ORDER BY ..., state_code`) to the SQL so every run produces identical files. Before that, tied states could swap places between runs.
- Labeled the standards as analyst-defined, not official CMS rules.

**Questions I must be able to answer**
1. What is an SLA, and why did I choose 10 minutes and 5%?
2. How does the miss-streak query work?
3. What does "automated" mean in this project?

**My answers**
1. An SLA is a service standard a team promises to meet. 10 minutes sits between the large-state peer average (6.3) and the national average (14.4). 5% is a common call-center abandonment target. Both are in a config file, so they're easy to change.
2. It numbers each state's months in order, then numbers only the missed months. Subtracting the two gives the same value for months that are back to back (the "gaps and islands" method), so I can count each streak's length.
3. One command rebuilds everything from the raw files: cleaning, SQL, SLA report and checks. It stops with FAIL if something doesn't match, and it keeps a log, so the report could run every morning without anyone redoing the work by hand.
