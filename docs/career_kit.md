# Career Kit: Medicaid Access Monitor

Ready-to-use text for the resume, LinkedIn, applications and interviews. Edit anything so it sounds like you.

---

## Resume: project entry

**Medicaid Access Monitor** | Excel, Power Query, Python (pandas), SQL (DuckDB), Streamlit | [Live dashboard](https://medicaid-access-monitor.streamlit.app/) · [GitHub](https://github.com/villegasjv55/medicaid-access-monitor)

- Analyzed **154.7M Medicaid call-center calls** across 50 states + DC (CMS data, 2023–2024) to rank states on wait time and abandonment during Medicaid unwinding.
- Built a **Python cleaning pipeline** with 12 data-quality checks and an exceptions log (417 issues documented); reconciled totals across **Python, SQL and Excel with zero variance**.
- Created an **Excel reporting workbook** using Power Query, XLOOKUP, PivotTables with weighted calculated fields, a region slicer, a state scorecard with risk scores, and a reconciliation tab.
- Wrote **15 SQL queries** in DuckDB (CTEs, JOINs, window functions RANK/LAG/ROW_NUMBER) to answer 6 business questions.
- Published an **interactive Streamlit dashboard** (U.S. map, state ranking, Florida spotlight, filters) and a 2-page findings memo with 5 operational recommendations.
- Found that **Florida ranked 3rd worst of 50 reporting states**: callers waited ~31 minutes (2× national) and 37% hung up (~13.4M calls).

**Shorter version (3 bullets)**
- Analyzed 154.7M Medicaid call-center calls (CMS, 50 states, 2023–2024); found Florida's wait was 2× the national average with 37% of callers hanging up.
- Built a Python + SQL + Excel reporting pipeline with 12 data-quality checks and zero-variance reconciliation across all three tools.
- Published a live Streamlit dashboard and a findings memo with staffing, call-deflection and queue-management recommendations.

---

## LinkedIn post (copy, edit, add a dashboard screenshot)

> During Medicaid "unwinding" (2023–2024), millions of people had to renew their coverage, and many called their state for help.
>
> I analyzed CMS data on **154.7 million** of those calls across every state. What stood out:
> 📞 Florida callers waited **~31 minutes** on average, **2× the national average** and **5× the other large states**
> 📉 **37%** of Florida callers hung up before reaching anyone (about **13.4 million calls**)
> 📈 Call volume tracked the renewal calendar almost exactly (correlation 0.94), so the peaks were predictable
>
> I cleaned the data in Python (logging 417 data issues instead of hiding them), checked every total in SQL and Excel, built a reporting workbook with Power Query and PivotTables, and published an interactive dashboard.
>
> 🔗 Live dashboard: https://medicaid-access-monitor.streamlit.app/
> 💻 GitHub: https://github.com/villegasjv55/medicaid-access-monitor
>
> #DataAnalytics #Excel #SQL #Python #Medicaid #ContactCenter #PublicHealth

---

## Interview answers (practice out loud)

**"Tell me about a project you're proud of." (about 60 seconds)**
"I built the Medicaid Access Monitor, using real CMS data on Medicaid call centers during unwinding, when every state had to re-check everyone's eligibility. I cleaned about 16,000 raw rows in Python, logged 417 data problems instead of hiding them, and proved nothing was lost: the same 154.7 million calls went in and came out. I then built the reporting in Excel with Power Query and PivotTables, double-checked everything with SQL, and published a live dashboard. The main finding was that Florida ranked 3rd worst: callers waited about 31 minutes and 37% hung up. Since calls tracked renewals almost one-to-one, I recommended staffing to the renewal calendar, adding callbacks and cutting avoidable calls."

**"Tell me about a data problem you found."**
"Rhode Island's call volume dropped 86% in one month, from about 62,000 to 8,500. That isn't a real change in callers, so it was almost certainly a change in how they counted. I didn't delete or 'fix' it. I flagged it in an exceptions log and footnoted it, so anyone using the numbers knows the trend for that state isn't comparable."

**"How do you make sure your numbers are right?"**
"I never edit raw files, and I check control totals at every step. My Python, SQL and Excel versions all give exactly 867 state-months, 154,681,330 calls and 28,472,216 abandoned calls. I also reconciled two CMS sources against each other and listed all 89 values where they disagreed."

**"Why weighted averages?"**
"A simple average lets a small state with 20,000 calls count as much as Florida with 2 million. Weighting by calls means the average reflects what callers actually experienced."

**"Did you use AI?"**
"Yes. I used AI to help write code and draft documents, the way many analysts do now. I verified every number myself through the reconciliation checks, and I can walk you through any formula or query in the project."

**"What would you do differently?"**
"I'd add caller-level data if it existed, since monthly averages hide the range of waits, and I'd track how each state defines its call center so comparisons are fairer."

---

## 2-minute demo video script (record with QuickTime: File › New Screen Recording)

1. **(0:00–0:15)** GitHub README: "This is the Medicaid Access Monitor, a reporting project on Medicaid call-center access during unwinding, using real CMS data."
2. **(0:15–0:45)** Dashboard, Access Overview: "This map shows the average wait by state. Darker means longer. Nationally callers waited 14.4 minutes and 18.4% hung up." Hover over Florida.
3. **(0:45–1:10)** Florida Spotlight: "Florida ranked 3rd worst. Callers waited about 31 minutes, twice the nation and five times the other big states, and 37% hung up."
4. **(1:10–1:30)** Excel Reconciliation tab, then SQL Q01 output: "I built the reporting in Excel and SQL, and all three tools give the same totals. Every check passes."
5. **(1:30–1:50)** Findings memo: "My recommendations: staff to the renewal calendar, add callbacks, cut avoidable calls and manage to weekly targets."
6. **(1:50–2:00)** "Links are in the README. Thanks for watching."

Upload to YouTube as **Unlisted** (or to Loom), then add the link to the README and resume.
