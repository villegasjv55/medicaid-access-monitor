"""
Medicaid Access Monitor - one-command refresh
=============================================
Runs the whole reporting pipeline end to end, the way a reporting team would
schedule it every morning:

  [1/5] clean the raw CMS files            (python/clean_data.py)
  [2/5] run every SQL query Q01-Q19         (python/run_sql.py)
  [3/5] apply the SLA standards             (config/sla_config.json)
  [4/5] write the dated KPI report          (output/)
  [5/5] reconciliation checks, PASS/FAIL    (logs/pipeline_log.txt)

Run it from the project folder:
    python python/run_pipeline.py

SLA standards are analyst-defined illustrative targets, not official CMS rules.
"""

from datetime import date, datetime
from pathlib import Path
import json
import subprocess
import sys
import time

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
RESULTS = ROOT / "sql" / "results"
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"
OUTPUT.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

LOG_FILE = LOGS / "pipeline_log.txt"
TODAY = date.today().isoformat()
start = time.time()
log_lines = [f"\n===== Pipeline run {datetime.now():%Y-%m-%d %H:%M:%S} ====="]


def say(msg):
    print(msg)
    log_lines.append(msg)


def step(n, label, result):
    say(f"[{n}/5] {label:<34} {result}")


def finish(ok):
    say(f"{'Done' if ok else 'STOPPED'} in {time.time() - start:.1f}s. Log: logs/pipeline_log.txt")
    with LOG_FILE.open("a") as f:
        f.write("\n".join(log_lines) + "\n")
    sys.exit(0 if ok else 1)


def run_script(name):
    """Run one of the existing scripts. Stop the whole pipeline if it fails."""
    r = subprocess.run([sys.executable, str(ROOT / "python" / name)], cwd=ROOT,
                       capture_output=True, text=True)
    log_lines.append(f"--- output of {name} (last lines) ---")
    log_lines.extend(r.stdout.strip().splitlines()[-6:])
    if r.returncode != 0:
        say(f"FAIL: {name} stopped.\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
        finish(False)
    return r.stdout


# ---------------------------------------------------------------- 1. clean
run_script("clean_data.py")
cc = pd.read_csv(CLEAN / "call_center_monthly.csv")
step(1, "Cleaning raw CMS files", f"{len(cc)} state-months PASS")

# ---------------------------------------------------------------- 2. SQL
out = run_script("run_sql.py")
n_results = len(list(RESULTS.glob("Q*.csv")))
step(2, "Running SQL queries", f"{n_results} results saved PASS")

# ---------------------------------------------------------------- 3. SLA
sla = json.loads((ROOT / "config" / "sla_config.json").read_text())
WAIT, ABAND, STREAK = sla["wait_sla_max_min"], sla["abandon_sla_max_rate"], sla["streak_alert_months"]
q16 = pd.read_csv(RESULTS / "Q16.csv")
q17 = pd.read_csv(RESULTS / "Q17.csv")
q18 = pd.read_csv(RESULTS / "Q18.csv")
q19 = pd.read_csv(RESULTS / "Q19.csv")
ev = q16[q16["sla_evaluated"]]
overall_pct = round(100 * ev["sla_met"].mean(), 1)
wait_pct = round(100 * ev["wait_sla_met"].mean(), 1)
aband_pct = round(100 * ev["abandon_sla_met"].mean(), 1)
watch = q19[q19["on_watch_list"]]
step(3, "Applying SLA standards", f"wait<={WAIT:g} min, abandon<={ABAND:.0%}")

# ---------------------------------------------------------------- 4. report
latest = q16["report_month"].max()
last = q16[q16["report_month"] == latest][["state_code", "sla_met"]].rename(
    columns={"sla_met": "latest_month_sla_met"})
report = (q17.merge(last, on="state_code", how="left")
             .merge(q19[["state_code", "longest_miss_streak", "current_miss_streak", "on_watch_list"]],
                    on="state_code", how="left"))
for col in ["longest_miss_streak", "current_miss_streak"]:
    report[col] = report[col].fillna(0).astype(int)
report["on_watch_list"] = report["on_watch_list"].eq(True)
report.insert(0, "report_date", TODAY)
report_file = OUTPUT / f"kpi_report_{TODAY}.csv"
report.to_csv(report_file, index=False)

fl = report[report["state_code"] == "FL"].iloc[0]
first_m, last_m = q18.iloc[0], q18.iloc[-1]
worst = report.sort_values(["overall_sla_pct", "state_code"]).head(10)
summary = f"""# SLA Compliance Summary ({TODAY})

Data: CMS Medicaid & CHIP call-center metrics, {q16['report_month'].min()} to {latest}.
Standards (analyst-defined, illustrative, not official CMS rules; see config/sla_config.json):
average wait <= {WAIT:g} minutes and abandonment <= {ABAND:.0%}. A state-month meets the SLA only if both are met.

## Headline KPIs
| KPI | Value |
|---|---|
| State-months evaluated | {len(ev)} |
| Overall SLA compliance | {overall_pct}% |
| Wait-time SLA compliance | {wait_pct}% |
| Abandonment SLA compliance | {aband_pct}% |
| States on watch list ({STREAK}+ months missed in a row) | {len(watch)} |

## Trend
Overall compliance went from {first_m['overall_sla_pct']}% of states ({first_m['report_month']}) to {last_m['overall_sla_pct']}% ({last_m['report_month']}).

## Florida
Met the SLA in {int(fl['months_sla_met'])} of {int(fl['months_evaluated'])} months; longest miss streak {int(fl['longest_miss_streak'])} months.

## Lowest compliance (top 10)
| State | Months met | Overall % | Wait % | Abandon % |
|---|---|---|---|---|
""" + "\n".join(f"| {r.state_name} | {r.months_sla_met}/{r.months_evaluated} | {r.overall_sla_pct} | {r.wait_sla_pct} | {r.abandon_sla_pct} |"
               for r in worst.itertuples()) + "\n"
(OUTPUT / "sla_summary.md").write_text(summary)
step(4, "Writing KPI report", f"output/{report_file.name}")

# ---------------------------------------------------------------- 5. checks
q01 = pd.read_csv(RESULTS / "Q01.csv").iloc[0]
both = cc["avg_wait_min"].notna() & cc["abandon_rate"].notna()
py_met = (cc["avg_wait_min"] <= WAIT) & (cc["abandon_rate"] <= ABAND) & both
checks = [
    ("State-months: Python = SQL", len(cc) == q01["state_months"]),
    ("Total calls: Python = SQL", cc["call_volume"].sum() == q01["total_calls"]),
    ("Q16 has one row per state-month", len(q16) == len(cc)),
    ("Evaluated months: Python = SQL", both.sum() == q16["sla_evaluated"].sum()),
    ("SLA-met months: Python = SQL", py_met.sum() == ev["sla_met"].sum()),
    ("By-state totals (Q17) = Q16", q17["months_sla_met"].sum() == ev["sla_met"].sum()
                                    and q17["months_evaluated"].sum() == len(ev)),
    ("By-month totals (Q18) = Q16", q18["states_sla_met"].sum() == ev["sla_met"].sum()
                                    and q18["states_evaluated"].sum() == len(ev)),
    ("Compliance % between 0 and 100", q17["overall_sla_pct"].between(0, 100).all()
                                       and q18["overall_sla_pct"].between(0, 100).all()),
    ("Streaks never longer than months", (q19["longest_miss_streak"] <= q16["report_month"].nunique()).all()),
    ("KPI report has one row per state", report["state_code"].is_unique and len(report) == len(q17)),
]
passed = sum(bool(ok) for _, ok in checks)
for name, ok in checks:
    log_lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
step(5, "Reconciliation checks", f"{passed}/{len(checks)} {'PASS' if passed == len(checks) else 'FAIL'}")
say(f"Headline: overall SLA compliance {overall_pct}% | watch list {len(watch)} states | Florida met {int(fl['months_sla_met'])}/{int(fl['months_evaluated'])} months")
finish(passed == len(checks))
