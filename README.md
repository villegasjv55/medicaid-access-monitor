# Medicaid Access Monitor
### Contact Center Performance Intelligence | Villegas Analytics

> **Status: in progress.** Phase 1 (data and scope) is complete. Finished results, the live dashboard link and screenshots will be added as each phase is completed.

## The question
**Which states left Medicaid callers waiting the longest during "unwinding," and what does that say about people's access to coverage?**

From 2023 to 2024, when the COVID-era continuous-enrollment rule ended, every state had to re-check the Medicaid eligibility of everyone enrolled. Millions of people called state Medicaid call centers to renew their coverage. CMS (Centers for Medicare & Medicaid Services) collects monthly call-center figures from every state. This project uses those figures to measure how well each state's call center answered the public, find which states struggled, and turn that into reports and recommendations a manager could act on.

## What this project includes
| # | Deliverable | Folder | Status |
|---|---|---|---|
| 1 | Excel reporting engine (Power Query, PivotTable scorecards, weighted KPIs, reconciliation tab) | `excel/` | Planned |
| 2 | Python cleaning script and data quality log | `python/`, `docs/` | Next |
| 3 | SQL query pack (15 documented DuckDB queries) | `sql/` | Planned |
| 4 | Interactive Streamlit dashboard (U.S. map, Florida spotlight, trends) | `dashboard/` | Planned |
| 5 | Findings memo (2 pages, consulting style) | `docs/` | Planned |
| 6 | Rollout simulation (**simulated scenario**) | `simulation/` | Planned |
| 7 | Executive briefing (7 slides) | `presentation/` | Planned |
| 8 | Learning log | `learning-log/` | Ongoing |

## Data
Real, public data from CMS, covering **March 2023 – July 2024 (17 months), 50 states + DC**:
- **Medicaid and CHIP CAA Reporting Metrics** (October 2024 release): the main source. Monthly call-center volume, average wait time and abandonment rate by state, plus renewals and procedural terminations.
- **State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data** (Performance Indicator dataset, March 2026 release): enrollment and applications, used to compare states fairly, plus a later-revised copy of the call-center figures used for reconciliation.

See [`docs/project_charter.md`](docs/project_charter.md), [`docs/data_sources.md`](docs/data_sources.md) and [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Repository structure
cd ~/Desktop/medicaid-access-monitor
cat > README.md <<'VILLEGAS_EOF'
# Medicaid Access Monitor
### Contact Center Performance Intelligence | Villegas Analytics

> **Status: in progress.** Phase 1 (data and scope) is complete. Finished results, the live dashboard link and screenshots will be added as each phase is completed.

## The question
**Which states left Medicaid callers waiting the longest during "unwinding," and what does that say about people's access to coverage?**

From 2023 to 2024, when the COVID-era continuous-enrollment rule ended, every state had to re-check the Medicaid eligibility of everyone enrolled. Millions of people called state Medicaid call centers to renew their coverage. CMS (Centers for Medicare & Medicaid Services) collects monthly call-center figures from every state. This project uses those figures to measure how well each state's call center answered the public, find which states struggled, and turn that into reports and recommendations a manager could act on.

## What this project includes
| # | Deliverable | Folder | Status |
|---|---|---|---|
| 1 | Excel reporting engine (Power Query, PivotTable scorecards, weighted KPIs, reconciliation tab) | `excel/` | Planned |
| 2 | Python cleaning script and data quality log | `python/`, `docs/` | Next |
| 3 | SQL query pack (15 documented DuckDB queries) | `sql/` | Planned |
| 4 | Interactive Streamlit dashboard (U.S. map, Florida spotlight, trends) | `dashboard/` | Planned |
| 5 | Findings memo (2 pages, consulting style) | `docs/` | Planned |
| 6 | Rollout simulation (**simulated scenario**) | `simulation/` | Planned |
| 7 | Executive briefing (7 slides) | `presentation/` | Planned |
| 8 | Learning log | `learning-log/` | Ongoing |

## Data
Real, public data from CMS, covering **March 2023 – July 2024 (17 months), 50 states + DC**:
- **Medicaid and CHIP CAA Reporting Metrics** (October 2024 release): the main source. Monthly call-center volume, average wait time and abandonment rate by state, plus renewals and procedural terminations.
- **State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data** (Performance Indicator dataset, March 2026 release): enrollment and applications, used to compare states fairly, plus a later-revised copy of the call-center figures used for reconciliation.

See [`docs/project_charter.md`](docs/project_charter.md), [`docs/data_sources.md`](docs/data_sources.md) and [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Repository structure
~~~
data/raw/          untouched original CMS downloads (never edited)
data/clean/        clean tables + exceptions log produced by python/clean_data.py
docs/              charter, data sources, data dictionary, quality report, memo
docs/reference/    CMS Unwinding Operations Snapshot PDFs used for reconciliation
excel/             Excel reporting engine
sql/               DuckDB query pack
python/            cleaning and data quality scripts
dashboard/         Streamlit app
simulation/        clearly labeled rollout simulation
presentation/      executive briefing deck
screenshots/       proof screenshots
learning-log/      notes on what I learned and why I made each decision
~~~

## Tools
Excel (Power Query, PivotTables) · Python (pandas) · DuckDB SQL · Streamlit + Plotly · GitHub

## Honesty notes
- All results come from real public CMS data. Any rollout figures are a **clearly labeled simulation**.
- States define "call center" differently, so comparisons between states have limits. These are documented in the data quality report.
- This is an independent portfolio project. It is not affiliated with or used by CMS or any state.

---
Built by Juan Villegas · [github.com/villegasjv55](https://github.com/villegasjv55)
