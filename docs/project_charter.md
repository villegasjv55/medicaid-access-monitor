# Project Charter: Medicaid Access Monitor

**Owner:** Juan Villegas · **Version:** 1.1 · **Date:** November 7, 2026

## Problem
When the COVID-era continuous-enrollment rule ended in 2023, every state had to re-check Medicaid eligibility for everyone enrolled ("unwinding"). Millions of people called state Medicaid call centers to renew. Some states answered quickly, while others had long hold times and many callers hanging up. CMS sent letters to several states raising concerns about wait times and abandonment rates. When people can't get through on the phone, eligible people can lose coverage for paperwork reasons.

## Audience
A **state Medicaid operations director** who needs to know how their call center performed, how it compares with other states, and what to fix.

## The 6 questions
1. Nationally, how did call volume, wait time and abandonment change month by month during unwinding?
2. Which 10 states had the worst weighted wait times and abandonment rates, and were they bad consistently or only in one month?
3. How did Florida compare with the national weighted average and with peer large states (TX, CA, NY, GA, PA)?
4. Did spikes in call volume line up with spikes in renewals?
5. Do states with worse call-center access also have higher procedural termination shares? (correlation only)
6. Which states improved the most from their peak, and what does that suggest is possible?

## In scope
- All 50 states + DC. South Dakota has no call center, so it is kept in the data but left out of call-center rankings.
- 17 reporting months: **March 2023 to July 2024**, the full period covered by the CMS CAA Reporting Metrics (October 2024 release).
- Three call-center metrics (call volume, average wait time, abandonment rate), plus enrollment, renewals and procedural terminations for context.
- Weighted national KPIs, state rankings, a Florida spotlight and an access risk score of my own design.

## Out of scope
- Individual-level or caller-level data (none is public).
- Causal claims. The project can show that two things happened together, not that one caused the other.
- Territories, and anything after the CMS reporting period.
- The rollout simulation is a **made-up scenario** for practice and is labeled as one everywhere.

## Deliverables
Excel reporting engine · Python cleaning script + exceptions log · data quality report · 15-query SQL pack · Streamlit dashboard · 2-page findings memo · rollout simulation pack · 7-slide executive briefing · README + demo videos · learning log.

## Success criteria
- The same KPIs give the same answer in Excel, SQL and the dashboard (reconciled).
- Every changed or excluded row is in the exceptions log; row counts and control totals match.
- Every number in the memo, deck and README comes from my own results.

## Known risks and limits
- States define "call center" differently, so straight comparisons are limited.
- Wait time is reported in whole minutes (under about 30 seconds shows as 0).
- Some values are blank: South Dakota (no call center, all months) and Nevada (November 2023 volume and abandonment).
- Possible reporting method changes (for example, Rhode Island call volume falls about 86% between April and May 2023).
- CMS later revised some call-center values in the Performance Indicator dataset (mainly Hawaii and Nebraska). The CAA release is used as the official record, and the differences are reconciled.
- CMS may revise recent months, so the file version and download date are recorded.
