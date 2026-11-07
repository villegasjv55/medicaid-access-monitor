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
2. Call volume (how many people called), average wait ticd ~/Desktop/medicaid-access-monitor
cat > learning-log/LEARNING_LOG.md <<'VILLEGAS_EOF'
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
