"""
Medicaid Access Monitor - Phase 2 cleaning script
=================================================
What this script does, in simple words:
  1. Reads the two untouched CMS files in data/raw/ (never changes them).
  2. Builds two clean tables with short standard names:
       data/clean/call_center_monthly.csv   (one row per state per month)
       data/clean/enrollment_monthly.csv    (one row per state per month)
  3. Runs quality checks and writes EVERY problem or change to
       data/clean/exceptions_log.csv
  4. Compares CMS's two copies of the call-center numbers and writes
       data/clean/reconciliation_caa_vs_pi.csv
  5. Proves nothing was lost: row counts and control totals must match,
     or the script stops with an error.

Run it from the project folder:
    python python/clean_data.py
Running it again always gives exactly the same result.
"""

from pathlib import Path
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# 0. SETTINGS
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]          # the project folder
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

CAA_FILE = "medicaid-chip-caa-reporting-metrics-long-table-october-2024-release.csv"
PI_FILE = "pi-dataset-march-2026release.csv"

# Unwinding reporting months covered by the CAA release
FIRST_MONTH = pd.Timestamp("2023-03-01")
LAST_MONTH = pd.Timestamp("2024-07-01")

# 50 states + DC
VALID_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}

# Exact CMS metric names (from the data dictionary) -> our short names
CALL_METRICS = {
    "Total call center volume (number of calls)": "call_volume",
    "Average call center wait time (minutes)": "avg_wait_min",
    "Average call center abandonment rate": "abandon_rate",
}
RENEWAL_METRICS = {
    "Total number of beneficiaries due for renewal in the reporting month (Metric 5)": "renewals_due",
    "Total beneficiaries whose coverage was terminated for a procedural or administrative reason (Metric 5c)": "terminated_procedural",
}

# Allowed ranges (outside these = logged, never silently changed)
RANGES = {
    "call_volume": (0, None),
    "avg_wait_min": (0, 180),
    "abandon_rate": (0, 1),
}
BIG_JUMP = 2.0   # month-over-month change above +200% (or a drop to under a third) gets flagged

# Every problem or change goes in here, then into exceptions_log.csv
exceptions = []


def log(state, month, check, field, original, action):
    """Add one line to the exceptions log."""
    exceptions.append({
        "state_code": state,
        "report_month": month.strftime("%Y-%m-%d") if isinstance(month, pd.Timestamp) else month,
        "check_name": check,
        "field": field,
        "original_value": original,
        "action_taken": action,
    })


def to_month(yyyymm):
    """Turn '202307' into the date 2023-07-01."""
    return pd.to_datetime(yyyymm.astype(str).str.strip(), format="%Y%m")


# ---------------------------------------------------------------------------
# 1. READ THE RAW FILES (as text, so nothing is changed on the way in)
# ---------------------------------------------------------------------------
caa_raw = pd.read_csv(RAW / CAA_FILE, dtype=str, keep_default_na=False)
pi_raw = pd.read_csv(RAW / PI_FILE, dtype=str, keep_default_na=False)
print(f"Read {CAA_FILE}: {len(caa_raw):,} rows")
print(f"Read {PI_FILE}: {len(pi_raw):,} rows")

# Two CAA headers end with a space ('Metric name ', 'Value '). Strip all headers.
caa = caa_raw.copy()
caa.columns = [c.strip() for c in caa.columns]
caa = caa.rename(columns={
    "State": "state_code", "Reporting period": "period", "Release date": "release",
    "Metric name": "metric", "Value": "value", "Data notes": "note",
})
for col in ["state_code", "period", "release", "metric", "value", "note"]:
    caa[col] = caa[col].str.strip()
caa["row_id"] = caa.index + 2          # +2 = line number in the CSV (header is line 1)
caa["report_month"] = to_month(caa["period"])
caa["release_month"] = to_month(caa["release"])

# Blank text -> missing. Then convert numbers.
caa["value_num"] = pd.to_numeric(caa["value"].replace({"": None, "NR": None, "-": None}), errors="coerce")

# ---------------------------------------------------------------------------
# 2. CALL CENTER TABLE
# ---------------------------------------------------------------------------
cc_long = caa[caa["metric"].isin(CALL_METRICS)].copy()
cc_long["field"] = cc_long["metric"].map(CALL_METRICS)
raw_cc_rows = len(cc_long)
raw_volume_total = cc_long.loc[cc_long["field"] == "call_volume", "value_num"].sum()
print(f"\nCall-center rows in raw file: {raw_cc_rows:,} (3 metrics per state-month)")

# Check: valid state (50 + DC). Anything else is logged and excluded.
bad_state = ~cc_long["state_code"].isin(VALID_STATES)
for _, r in cc_long[bad_state].iterrows():
    log(r.state_code, r.report_month, "valid_state", r.field, r.value, "excluded: not one of 50 states + DC")

# Check: month inside the unwinding range
bad_month = ~cc_long["report_month"].between(FIRST_MONTH, LAST_MONTH)
for _, r in cc_long[bad_month & ~bad_state].iterrows():
    log(r.state_code, r.report_month, "date_range", r.field, r.value, "excluded: outside Mar 2023 - Jul 2024")

excluded_long = cc_long[bad_state | bad_month]
cc_long = cc_long[~(bad_state | bad_month)]

# Check: duplicates (one value per state + month + metric)
dup = cc_long.duplicated(["state_code", "report_month", "field"], keep="first")
for _, r in cc_long[dup].iterrows():
    log(r.state_code, r.report_month, "duplicate", r.field, r.value, "excluded: duplicate row, first one kept")
excluded_long = pd.concat([excluded_long, cc_long[dup]])
cc_long = cc_long[~dup]

# Pivot: turn 3 rows per state-month into 1 row with 3 columns
cc = cc_long.pivot(index=["state_code", "report_month"], columns="field", values="value_num").reset_index()
cc.columns.name = None

# Keep CMS notes (one per metric) and the release month
notes = (cc_long.assign(tagged=cc_long["field"] + ": " + cc_long["note"])
         .loc[cc_long["note"] != ""]
         .groupby(["state_code", "report_month"])["tagged"].apply(" | ".join)
         .rename("data_note").reset_index())
release = cc_long.groupby(["state_code", "report_month"])["release_month"].first().reset_index()
cc = cc.merge(notes, how="left").merge(release, how="left")
cc["data_note"] = cc["data_note"].fillna("")

# Check: missing values. Mark is_reported = False and log them (never fill them in).
cc["is_reported"] = cc[list(CALL_METRICS.values())].notna().all(axis=1)
for _, r in cc.iterrows():
    for f in CALL_METRICS.values():
        if pd.isna(r[f]):
            log(r.state_code, r.report_month, "missing_value", f, "",
                "kept as blank; is_reported = False; excluded from KPIs for this metric")

# Check: ranges (log only, never change the number)
for f, (lo, hi) in RANGES.items():
    out = cc[f].notna() & ((cc[f] < lo) | ((cc[f] > hi) if hi is not None else False))
    for _, r in cc[out].iterrows():
        log(r.state_code, r.report_month, "range", f, r[f], f"flagged: outside {lo} to {hi}; value not changed")

# Check: 0-minute waits (CMS rounds under ~30 seconds down to 0)
for _, r in cc[cc["avg_wait_min"] == 0].iterrows():
    log(r.state_code, r.report_month, "zero_wait", "avg_wait_min", 0,
        "kept: 0 means under about 30 seconds (whole-minute rounding), not 'no wait'")

# Check: big month-over-month jumps in call volume
cc = cc.sort_values(["state_code", "report_month"]).reset_index(drop=True)
prev = cc.groupby("state_code")["call_volume"].shift(1)
ratio = cc["call_volume"] / prev
jump = ratio.notna() & ((ratio > 1 + BIG_JUMP) | (ratio < 1 / (1 + BIG_JUMP)))
for i in cc[jump].index:
    r = cc.loc[i]
    log(r.state_code, r.report_month, "big_jump", "call_volume",
        f"{prev[i]:,.0f} -> {r.call_volume:,.0f} ({ratio[i] - 1:+.0%})",
        "flagged for review: check CMS notes for a reporting change; value not changed")

# Add state names from the PI file
names = pi_raw[["State Abbreviation", "State Name"]].drop_duplicates()
names.columns = ["state_code", "state_name"]
cc = cc.merge(names, how="left")
cc["source_file"] = CAA_FILE

cc = cc[["state_code", "state_name", "report_month", "call_volume", "avg_wait_min",
         "abandon_rate", "is_reported", "data_note", "release_month", "source_file"]]
cc["call_volume"] = cc["call_volume"].astype("Int64")

# ---- Row-count and control-total checks (stop if anything was lost) ----
rows_in = raw_cc_rows
rows_out = len(cc) * 3
rows_excluded = len(excluded_long)
if rows_in != rows_out + rows_excluded:
    sys.exit(f"STOP: row counts do not match: {rows_in} in vs {rows_out} out + {rows_excluded} excluded")
print(f"Row count OK: {rows_in:,} raw rows = {rows_out:,} kept + {rows_excluded:,} excluded "
      f"-> {len(cc):,} clean state-months")

clean_total = cc["call_volume"].sum()
excl_total = excluded_long.loc[excluded_long["field"] == "call_volume", "value_num"].sum()
if abs(raw_volume_total - (clean_total + excl_total)) >= 1:
    sys.exit(f"STOP: control totals do not match: {raw_volume_total:,.0f} vs {clean_total + excl_total:,.0f}")
print(f"Control total OK: {raw_volume_total:,.0f} calls (raw) = {clean_total:,.0f} clean + {excl_total:,.0f} excluded")

# ---------------------------------------------------------------------------
# 3. ENROLLMENT TABLE
# ---------------------------------------------------------------------------
pi = pi_raw.copy()
pi["report_month"] = to_month(pi["Reporting Period"])
pi = pi[pi["report_month"].between(FIRST_MONTH, LAST_MONTH)]
n_prelim = (pi["Preliminary or Updated"] == "P").sum()
pi = pi[pi["Preliminary or Updated"] == "U"]          # keep the revised version only
print(f"\nPI file: kept {len(pi):,} Updated rows for Mar 2023 - Jul 2024, dropped {n_prelim:,} Preliminary duplicates")
if pi.duplicated(["State Abbreviation", "report_month"]).any():
    sys.exit("STOP: PI file still has more than one Updated row for a state-month")

enr = pd.DataFrame({
    "state_code": pi["State Abbreviation"].str.strip(),
    "report_month": pi["report_month"],
    "total_enrollment": pd.to_numeric(pi["Total Medicaid and CHIP Enrollment"], errors="coerce"),
    "applications_received": pd.to_numeric(pi["New Applications Submitted to Medicaid and CHIP Agencies"], errors="coerce"),
})

ren = caa[caa["metric"].isin(RENEWAL_METRICS) & caa["state_code"].isin(VALID_STATES)].copy()
ren["field"] = ren["metric"].map(RENEWAL_METRICS)
ren = ren.pivot(index=["state_code", "report_month"], columns="field", values="value_num").reset_index()
ren.columns.name = None

enr = cc[["state_code", "report_month"]].merge(enr, how="left").merge(ren, how="left")
for f in ["total_enrollment", "applications_received", "renewals_due", "terminated_procedural"]:
    for _, r in enr[enr[f].isna()].iterrows():
        log(r.state_code, r.report_month, "missing_value", f, "", "kept as blank; excluded from KPIs that need it")
    enr[f] = enr[f].astype("Int64")
enr["source_file"] = f"{PI_FILE} (enrollment, applications); {CAA_FILE} (renewals, terminations)"

# ---------------------------------------------------------------------------
# 4. RECONCILIATION: CAA (official unwinding record) vs PI (later revised copy)
# ---------------------------------------------------------------------------
pi_cc = pd.DataFrame({
    "state_code": pi["State Abbreviation"].str.strip(),
    "report_month": pi["report_month"],
    "call_volume": pd.to_numeric(pi["Total Call Center Volume (Number of Calls)"], errors="coerce"),
    "avg_wait_min": pd.to_numeric(pi["Average Call Center Wait Time (Minutes)"], errors="coerce"),
    "abandon_rate": pd.to_numeric(pi["Average Call Center Abandonment Rate"], errors="coerce"),
})
both = cc.merge(pi_cc, on=["state_code", "report_month"], how="left", suffixes=("_caa", "_pi"))
recon = []
for f in CALL_METRICS.values():
    a, b = both[f + "_caa"].astype("float"), both[f + "_pi"].astype("float")
    differs = ~((a == b) | (a.isna() & b.isna()))
    for i in both[differs].index:
        r = both.loc[i]
        recon.append({"state_code": r.state_code, "report_month": r.report_month.strftime("%Y-%m-%d"),
                      "field": f, "caa_value": a[i], "pi_value": b[i]})
        log(r.state_code, r.report_month, "reconciliation_caa_vs_pi", f, f"CAA={a[i]} PI={b[i]}",
            "kept CAA value (official unwinding record); PI was revised later")
recon = pd.DataFrame(recon, columns=["state_code", "report_month", "field", "caa_value", "pi_value"])

# ---------------------------------------------------------------------------
# 5. SAVE EVERYTHING
# ---------------------------------------------------------------------------
for df in (cc, enr):
    df["report_month"] = df["report_month"].dt.strftime("%Y-%m-%d")
cc["release_month"] = pd.to_datetime(cc["release_month"]).dt.strftime("%Y-%m-%d")

exc = pd.DataFrame(exceptions)
exc.insert(0, "exception_id", range(1, len(exc) + 1))

cc.to_csv(CLEAN / "call_center_monthly.csv", index=False)
enr.to_csv(CLEAN / "enrollment_monthly.csv", index=False)
exc.to_csv(CLEAN / "exceptions_log.csv", index=False)
recon.to_csv(CLEAN / "reconciliation_caa_vs_pi.csv", index=False)

print("\nSaved to data/clean/:")
print(f"  call_center_monthly.csv       {len(cc):>5} rows  ({cc['is_reported'].sum()} fully reported)")
print(f"  enrollment_monthly.csv        {len(enr):>5} rows")
print(f"  exceptions_log.csv            {len(exc):>5} rows")
print(f"  reconciliation_caa_vs_pi.csv  {len(recon):>5} rows")
print("\nExceptions by check:")
print(exc["check_name"].value_counts().to_string())
print("\nDONE: all checks passed.")
