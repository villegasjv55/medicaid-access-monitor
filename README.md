# Medicaid Access Monitor
### Contact Center Performance Intelligence | Villegas Analytics

[![Live dashboard](https://img.shields.io/badge/Live%20dashboard-Open%20app-8F3358?style=for-the-badge)](https://medicaid-access-monitor.streamlit.app/)
![Data](https://img.shields.io/badge/Data-CMS%20public%20data-1F3A5F?style=for-the-badge)
![Tools](https://img.shields.io/badge/Excel%20·%20Python%20·%20SQL%20·%20Streamlit-2A7F8E?style=for-the-badge)

**Which states left Medicaid callers waiting the longest during "unwinding," and what does that say about people's access to coverage?**

🔗 **Live dashboard:** https://medicaid-access-monitor.streamlit.app/

---

## Key findings (March 2023 – July 2024, 50 reporting states + DC)

- **Florida ranked 3rd worst of 50 reporting states** for call-center access, behind Missouri and Montana.
- Florida callers waited **about 31 minutes** on average: **2× the national average (14.4 min)** and **5× the other large states (6.3 min)**. Florida's wait was over 15 minutes in **all 17 months**.
- **37% of Florida callers hung up** before reaching anyone, about **13.4 million calls**, against 18.4% nationally.
- Florida handled **23% of all Medicaid call-center calls in the U.S.** and had the highest call load in the country (486.7 calls per 1,000 enrollees per month).
- Nationally, the **worst month was July 2023** (20.2-minute weighted wait, 22.6% hung up). Call volume rose and fell with renewals (correlation 0.94).
- **Recovery is possible:** several states cut waits by 30+ minutes from their peak (Maine 44 → 5.7, Idaho 56 → 18.7, Oklahoma 46 → 9.7).

## The story in brief

From 2023 to 2024, when the COVID-era continuous-enrollment rule ended, every state had to re-check the Medicaid eligibility of everyone enrolled. Millions of people called state call centers to renew their coverage. CMS published monthly call-center figures for every state. This project cleans those figures, proves the numbers are right, and turns them into reports, a dashboard and recommendations a Medicaid operations director could act on.

## What I built

| # | Deliverable | Where | Status |
|---|---|---|---|
| 1 | **Python cleaning pipeline:** tidy tables, 12 quality checks, exceptions log (417 entries), CAA vs PI reconciliation | [`python/clean_data.py`](python/clean_data.py), [`data/clean/`](data/clean/) | ✅ |
| 2 | **Data quality report** | [`docs/data_quality_report.md`](docs/data_quality_report.md) | ✅ |
| 3 | **Excel reporting engine:** Power Query (documented steps), Calc table with XLOOKUP, PivotTable with weighted calculated fields, PivotChart, region slicer, state scorecard with risk score, Florida spotlight, reconciliation tab | [`excel/Medicaid_Access_Reporting.xlsx`](excel/) | ✅ |
| 4 | **SQL query pack:** 15 DuckDB queries (GROUP BY, JOINs, CTEs, window functions RANK / LAG / ROW_NUMBER, CORR) | [`sql/`](sql/) | ✅ |
| 5 | **Interactive dashboard:** U.S. map, state ranking, Florida spotlight, state comparison, filters | [`dashboard/app.py`](dashboard/app.py) · [live](https://medicaid-access-monitor.streamlit.app/) | ✅ |
| 6 | Findings memo (2 pages) | `docs/` | Next |
| 7 | Rollout simulation (**clearly labeled simulation**) | `simulation/` | Planned |
| 8 | Executive briefing (7 slides) + demo video | `presentation/` | Planned |
| 9 | Learning log | [`learning-log/`](learning-log/) | Ongoing |

## How I made sure the numbers are right

- **Raw files are never edited.** Every change happens in code and is logged.
- **Control totals match across all three tools:**

| Check | Python | SQL | Excel |
|---|---|---|---|
| State-months | 867 | 867 | 867 |
| Total calls | 154,681,330 | 154,681,330 | 154,681,330 |
| Abandoned calls | 28,472,216 | 28,472,216 | 28,472,216 |

- **417 data issues logged, none hidden.** For example: South Dakota has no call center (excluded from rankings, not treated as zero); Rhode Island's call volume fell 86% in one month (a counting change, flagged); 79 months show a 0-minute wait (whole-minute rounding).
- **Two CMS copies reconciled:** 89 values differ between the official CAA release and the later-revised PI dataset (mostly Nebraska and Hawaii). The CAA values are used and every difference is listed.

## Data

Real, public CMS data:
- **Medicaid and CHIP CAA Reporting Metrics** (October 2024 release): the main source.
- **State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data** (Performance Indicator dataset, March 2026 release): enrollment, applications and reconciliation.

Details: [`docs/project_charter.md`](docs/project_charter.md) · [`docs/data_sources.md`](docs/data_sources.md) · [`docs/data_dictionary.md`](docs/data_dictionary.md)

## Run it yourself

~~~
pip install -r requirements.txt
python python/clean_data.py      # rebuild the clean tables + exceptions log
python python/run_sql.py         # run the 15 SQL queries
streamlit run dashboard/app.py   # open the dashboard locally
~~~

## Repository structure

~~~
data/raw/          untouched original CMS downloads (never edited)
data/clean/        clean tables, exceptions log, reconciliation
data/lookup/       state regions and peer groups
docs/              charter, data sources, data dictionary, quality report
excel/             Excel reporting workbook
sql/               DuckDB query pack + results
python/            cleaning pipeline and SQL runner
dashboard/         Streamlit app
learning-log/      what I learned and why I made each decision
~~~

## Honesty notes

- All results come from real public CMS data. Any rollout figures will be a **clearly labeled simulation**.
- States define "call center" differently, so comparisons show broad patterns, not exact rankings.
- Findings show patterns, not causes.
- Built with AI assistance for code and drafting; every data check, reconciliation and finding was verified by me.
- Independent portfolio project, not affiliated with CMS or any state.

---
Built by **Juan Villegas** · [github.com/villegasjv55](https://github.com/villegasjv55)
