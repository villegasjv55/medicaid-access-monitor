"""
Medicaid Access Monitor - Phase 4 SQL runner
============================================
Loads the clean CSVs into an in-memory DuckDB database, runs every query in
sql/queries.sql, prints each result, and saves each one to sql/results/Q##.csv.

Run it from the project folder:
    python python/run_sql.py
"""

from pathlib import Path
import re

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "sql" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

con = duckdb.connect()
con.execute(f"CREATE VIEW cc AS SELECT * FROM read_csv_auto('{ROOT / 'data/clean/call_center_monthly.csv'}')")
con.execute(f"CREATE VIEW enr AS SELECT * FROM read_csv_auto('{ROOT / 'data/clean/enrollment_monthly.csv'}')")
con.execute(f"CREATE VIEW states AS SELECT * FROM read_csv_auto('{ROOT / 'data/lookup/lookup_states.csv'}')")

text = (ROOT / "sql" / "queries.sql").read_text()
# Split on the "-- Q##: title" header lines
parts = re.split(r"^-- (Q\d{2}): (.*)$", text, flags=re.MULTILINE)
queries = [(parts[i], parts[i + 1].strip(), parts[i + 2].strip()) for i in range(1, len(parts), 3)]

print(f"Running {len(queries)} queries...\n")
for qid, title, sql in queries:
    df = con.execute(sql).df()
    # Show whole-number columns without ".0" (e.g. 154681330 instead of 154681330.0)
    for col in df.columns:
        if df[col].dtype.kind == "f" and df[col].dropna().apply(float.is_integer).all():
            df[col] = df[col].astype("Int64")
    df.to_csv(RESULTS / f"{qid}.csv", index=False)
    print("=" * 90)
    print(f"{qid}: {title}   ({len(df)} rows)")
    print("-" * 90)
    print(df.to_string(index=False))
    print()

print(f"DONE: {len(queries)} queries ran. Results saved to sql/results/")
