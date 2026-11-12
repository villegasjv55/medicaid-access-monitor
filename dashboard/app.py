"""
Medicaid Access Monitor - Phase 5 dashboard (Streamlit)
=======================================================
Run on your computer (from the project folder):
    streamlit run dashboard/app.py
It reads the clean tables made by python/clean_data.py.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PEERS = ["TX", "CA", "NY", "GA", "PA"]

# Wine color steps (light = short waits, dark = long waits)
BINS = [(-1, 5, "Under 5 min"), (5, 10, "5–10 min"), (10, 15, "10–15 min"), (15, 20, "15–20 min"),
        (20, 25, "20–25 min"), (25, 30, "25–30 min"), (30, 999, "30+ min")]
WINE = ["#F3DCE4", "#E4B1C2", "#D0839E", "#B5577A", "#8F3358", "#661A3A", "#3E0A22"]
ACCENT = "#8F3358"

st.set_page_config(page_title="Medicaid Access Monitor", page_icon="📞", layout="wide")

# ---------------------------------------------------------------------------
# Look and feel (Power BI-style report page)
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
  #MainMenu, footer, header [data-testid="stToolbar"] {{visibility: hidden;}}
  .stApp {{background: #EEF0F3;}}
  .block-container {{padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1500px;}}
  section[data-testid="stSidebar"] {{background: #FFFFFF; border-right: 1px solid #E1E4E8;}}
  section[data-testid="stSidebar"] .stRadio label p {{font-size: 15px;}}
  .titlebar {{background: #FFFFFF; border-radius: 6px; padding: 14px 22px; margin-bottom: 14px;
             border-left: 6px solid {ACCENT}; box-shadow: 0 1px 3px rgba(0,0,0,.08);}}
  .titlebar h1 {{color: #3E2A5C; font-size: 28px; margin: 0; font-weight: 600;}}
  .titlebar p {{color: #6B7280; margin: 2px 0 0 0; font-size: 14px;}}
  .card {{background: #FFFFFF; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;
         box-shadow: 0 1px 3px rgba(0,0,0,.08);}}
  .card-title {{color: #6B7280; font-size: 12px; letter-spacing: .08em; text-transform: uppercase;
               border-bottom: 1px solid #E5E7EB; padding-bottom: 6px; margin-bottom: 8px;}}
  .big {{font-size: 38px; font-weight: 300; color: #1F2937; text-align: center; line-height: 1.1;}}
  .sub {{font-size: 13px; color: #6B7280; text-align: center;}}
  .row {{display: flex; justify-content: space-around; text-align: center;}}
  .row .v {{font-size: 22px; color: #1F2937;}}
  .row .l {{font-size: 12px; color: #6B7280;}}
  .bar {{height: 10px; border-radius: 5px; background: #E5E7EB; overflow: hidden; margin: 4px 0 2px 0;}}
  .bar > div {{height: 100%; background: {ACCENT};}}
  .section {{color: #4B5563; font-size: 14px; letter-spacing: .06em; text-transform: uppercase;
            margin: 2px 0 6px 2px;}}
  div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {{background: #FFFFFF; border-radius: 6px;
            padding: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.08);}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def load():
    cc = pd.read_csv(ROOT / "data/clean/call_center_monthly.csv", parse_dates=["report_month"])
    enr = pd.read_csv(ROOT / "data/clean/enrollment_monthly.csv", parse_dates=["report_month"])
    states = pd.read_csv(ROOT / "data/lookup/lookup_states.csv")
    df = cc.merge(enr[["state_code", "report_month", "total_enrollment"]], on=["state_code", "report_month"], how="left")
    df = df.merge(states[["state_code", "region", "peer_group"]], on="state_code", how="left")
    df["abandoned_calls"] = (df["call_volume"] * df["abandon_rate"]).round()
    df["wait_x_calls"] = df["call_volume"] * df["avg_wait_min"]
    return df


def weighted(d):
    """Weighted wait and abandonment: busier state-months count more."""
    d = d[d["call_volume"].notna()]
    calls = d["call_volume"].sum()
    return pd.Series({
        "calls": calls,
        "abandoned": d["abandoned_calls"].sum(),
        "weighted_wait": d["wait_x_calls"].sum() / calls if calls else float("nan"),
        "weighted_abandon": d["abandoned_calls"].sum() / calls if calls else float("nan"),
    })


def scorecard(d):
    s = d.groupby(["state_code", "state_name", "region"]).apply(weighted, include_groups=False).reset_index()
    peak = d.groupby("state_code")["avg_wait_min"].max().rename("peak_wait")
    over = d.groupby("state_code")["avg_wait_min"].apply(lambda x: (x > 15).sum()).rename("months_over_15")
    s = s.merge(peak, on="state_code").merge(over, on="state_code")
    s = s[s["calls"] > 0].copy()
    s["risk_score"] = (50 * s["weighted_wait"].rank(pct=True, method="min")
                       + 50 * s["weighted_abandon"].rank(pct=True, method="min")).round(0)
    s["rank"] = s["risk_score"].rank(ascending=False, method="min").astype(int)
    return s.sort_values("rank")


def wait_band(x):
    for lo, hi, name in BINS:
        if lo < x <= hi:
            return name
    return "No data"


def card(title, body):
    st.markdown(f'<div class="card"><div class="card-title">{title}</div>{body}</div>', unsafe_allow_html=True)


def bar(share):
    return f'<div class="bar"><div style="width:{max(0, min(1, share)) * 100:.0f}%"></div></div>'


def style_fig(fig, h):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white",
                      plot_bgcolor="white", font=dict(color="#374151"),
                      legend=dict(orientation="h", y=1.12, x=0))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF0F3")
    return fig


df_all = load()
all_months = sorted(df_all["report_month"].dt.to_pydatetime())

# ---------------------------------------------------------------------------
# Sidebar: pages + filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📞 Medicaid Access Monitor")
    st.caption("Villegas Analytics")
    st.markdown("**Pages**")
    page = st.radio("Pages", ["Access Overview", "State Ranking", "Florida Spotlight", "Compare States",
                              "About the Data"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Filters**")
    start, end = st.select_slider("Months", options=all_months, value=(all_months[0], all_months[-1]),
                                  format_func=lambda d: d.strftime("%b %Y"))
    regions = st.multiselect("Region", sorted(df_all["region"].unique()), default=sorted(df_all["region"].unique()))
    st.divider()
    st.caption("Real public CMS data · Mar 2023 – Jul 2024 · 50 states + DC")

df = df_all[(df_all["report_month"] >= pd.Timestamp(start)) & (df_all["report_month"] <= pd.Timestamp(end))]
df = df[df["region"].isin(regions)] if regions else df
score = scorecard(df)
national = weighted(df)
period = f"{pd.Timestamp(start):%b %Y} – {pd.Timestamp(end):%b %Y}"


def titlebar(title, subtitle):
    st.markdown(f'<div class="titlebar"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


if score.empty:
    titlebar("Medicaid Access Monitor", "No data for the selected filters.")
    st.stop()

fl_row = score[score["state_code"] == "FL"]

# ---------------------------------------------------------------------------
# Page 1: Access Overview
# ---------------------------------------------------------------------------
if page == "Access Overview":
    titlebar("Medicaid Call Center Access Dashboard",
             f"Which states left Medicaid callers waiting the longest during unwinding? · {period}")
    left, right = st.columns([3, 1.15], gap="medium")

    with left:
        st.markdown('<div class="section">Average wait on hold by state (weighted by calls)</div>',
                    unsafe_allow_html=True)
        m = score.copy()
        m["band"] = m["weighted_wait"].apply(wait_band)
        m["Wait (min)"] = m["weighted_wait"].round(1)
        m["Hung up"] = (100 * m["weighted_abandon"]).round(1).astype(str) + "%"
        m["Rank"] = m["rank"]
        order = [b[2] for b in BINS]
        fig = px.choropleth(
            m, locations="state_code", locationmode="USA-states", scope="usa", color="band",
            category_orders={"band": order}, color_discrete_map=dict(zip(order, WINE)),
            hover_name="state_name", hover_data={"state_code": False, "band": False, "Wait (min)": True,
                                                 "Hung up": True, "Rank": True},
        )
        fig.update_traces(marker_line_color="white", marker_line_width=0.8)
        fig = style_fig(fig, 470)
        fig.update_layout(geo=dict(bgcolor="white", lakecolor="white", showlakes=False),
                          legend=dict(title="", orientation="h", y=-0.02, x=0.5, xanchor="center",
                                      font=dict(size=11)))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        st.markdown('<div class="section">National trend: weighted wait and share of callers who hung up</div>',
                    unsafe_allow_html=True)
        nat = df.groupby("report_month").apply(weighted, include_groups=False)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=nat.index, y=nat["weighted_wait"], name="Weighted wait (min)",
                              marker_color="#E4B1C2"))
        fig2.add_trace(go.Scatter(x=nat.index, y=nat["weighted_abandon"], name="Hung up (%)", yaxis="y2",
                                  mode="lines+markers", line=dict(color=ACCENT, width=3)))
        fig2.update_layout(yaxis=dict(title="Minutes"),
                           yaxis2=dict(title="Hung up", overlaying="y", side="right", tickformat=".0%",
                                       showgrid=False))
        st.plotly_chart(style_fig(fig2, 260), width="stretch", config={"displayModeBar": False})

    with right:
        st.markdown('<div class="section">At a glance…</div>', unsafe_allow_html=True)
        card("Total calls to Medicaid call centers",
             f'<div class="big">{national["calls"] / 1e6:,.1f}M</div>'
             f'<div class="sub">{score["state_code"].nunique()} reporting states · {period}</div>')
        card("Average wait on hold",
             f'<div class="big">{national["weighted_wait"]:.1f} <span style="font-size:18px">min</span></div>'
             f'<div class="sub">weighted by call volume</div>')
        card("Callers who hung up",
             f'<div class="big">{national["weighted_abandon"]:.1%}</div>{bar(national["weighted_abandon"])}'
             f'<div class="sub">{national["abandoned"] / 1e6:,.1f}M calls abandoned</div>')
        top3 = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:3px 0;">'
            f'<span>#{r["rank"]} {r["state_name"]}</span><span>{r["weighted_wait"]:.1f} min</span></div>'
            for _, r in score.head(3).iterrows())
        card("Worst access (risk score)", top3)
        if not fl_row.empty:
            f = fl_row.iloc[0]
            card("Florida",
                 f'<div class="row"><div><div class="v">#{f["rank"]}</div><div class="l">rank</div></div>'
                 f'<div><div class="v">{f["weighted_wait"]:.0f}m</div><div class="l">wait</div></div>'
                 f'<div><div class="v">{f["weighted_abandon"]:.0%}</div><div class="l">hung up</div></div></div>')

# ---------------------------------------------------------------------------
# Page 2: State Ranking
# ---------------------------------------------------------------------------
elif page == "State Ranking":
    titlebar("State Ranking", f"Every reporting state ranked by risk score (1 = worst access) · {period}")
    left, right = st.columns([2.6, 1], gap="medium")
    with left:
        show = score[["rank", "state_name", "region", "calls", "weighted_wait", "weighted_abandon",
                      "peak_wait", "months_over_15", "risk_score"]].rename(columns={
            "rank": "Rank", "state_name": "State", "region": "Region", "calls": "Total calls",
            "weighted_wait": "Wait (min)", "weighted_abandon": "Hung up", "peak_wait": "Peak (min)",
            "months_over_15": "Months >15", "risk_score": "Risk score"})
        st.dataframe(
            show.style.format({"Total calls": "{:,.0f}", "Wait (min)": "{:.1f}", "Hung up": "{:.1%}",
                               "Peak (min)": "{:.0f}", "Risk score": "{:.0f}"})
            .background_gradient(subset=["Risk score"], cmap="RdPu"),
            hide_index=True, width="stretch", height=640)
    with right:
        top = score.head(10).sort_values("risk_score")
        fig = px.bar(top, x="risk_score", y="state_name", orientation="h", text="risk_score",
                     color_discrete_sequence=[ACCENT], labels={"risk_score": "Risk score", "state_name": ""})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, 125])
        st.markdown('<div class="section">Top 10 worst access</div>', unsafe_allow_html=True)
        st.plotly_chart(style_fig(fig, 420), width="stretch", config={"displayModeBar": False})
        card("How the risk score works",
             '<div class="sub" style="text-align:left">Half is based on weighted wait and half on the share '
             'of callers who hung up, each compared with the other states. 0 = best, 100 = worst. '
             'South Dakota has no call center and is left out.</div>')

# ---------------------------------------------------------------------------
# Page 3: Florida Spotlight
# ---------------------------------------------------------------------------
elif page == "Florida Spotlight":
    titlebar("Florida Spotlight", f"Florida vs the national average vs other large states (TX, CA, NY, GA, PA) · {period}")
    if fl_row.empty:
        st.warning("Florida is filtered out. Add the South region in the sidebar.")
        st.stop()
    f = fl_row.iloc[0]
    peers = weighted(df_all[(df_all["state_code"].isin(PEERS)) & df_all["report_month"].between(
        pd.Timestamp(start), pd.Timestamp(end))])
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        card("Florida rank", f'<div class="big">#{f["rank"]}</div><div class="sub">of {len(score)} states</div>')
    with k2:
        card("Average wait", f'<div class="big">{f["weighted_wait"]:.1f}m</div>'
                             f'<div class="sub">national {national["weighted_wait"]:.1f} · peers {peers["weighted_wait"]:.1f}</div>')
    with k3:
        card("Callers who hung up", f'<div class="big">{f["weighted_abandon"]:.0%}</div>{bar(f["weighted_abandon"])}'
                                    f'<div class="sub">{f["abandoned"] / 1e6:,.1f}M calls</div>')
    with k4:
        card("Share of U.S. calls", f'<div class="big">{f["calls"] / national["calls"]:.0%}</div>'
                                    f'<div class="sub">{f["calls"] / 1e6:,.1f}M calls</div>')

    flm = df[df["state_code"] == "FL"].set_index("report_month")
    nat = df.groupby("report_month").apply(weighted, include_groups=False)
    peer = df_all[df_all["state_code"].isin(PEERS) & df_all["report_month"].between(
        pd.Timestamp(start), pd.Timestamp(end))].groupby("report_month").apply(weighted, include_groups=False)
    c1, c2 = st.columns(2, gap="medium")
    for col, title, cols, fmt in [
        (c1, "Average wait (minutes)", ("avg_wait_min", "weighted_wait"), None),
        (c2, "Share of callers who hung up", ("abandon_rate", "weighted_abandon"), ".0%"),
    ]:
        with col:
            st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=flm.index, y=flm[cols[0]], name="Florida", mode="lines+markers",
                                     line=dict(color=ACCENT, width=3.5)))
            fig.add_trace(go.Scatter(x=nat.index, y=nat[cols[1]], name="National", mode="lines",
                                     line=dict(color="#D0839E", width=2)))
            fig.add_trace(go.Scatter(x=peer.index, y=peer[cols[1]], name="Large-state peers", mode="lines",
                                     line=dict(color="#9CA3AF", width=2, dash="dot")))
            if fmt:
                fig.update_yaxes(tickformat=fmt)
            st.plotly_chart(style_fig(fig, 360), width="stretch", config={"displayModeBar": False})
    card("What this means",
         f'<div class="sub" style="text-align:left;font-size:14px">Florida callers waited about '
         f'<b>{f["weighted_wait"]:.0f} minutes</b> on average, roughly <b>{f["weighted_wait"] / national["weighted_wait"]:.1f}×</b> '
         f'the national average and <b>{f["weighted_wait"] / peers["weighted_wait"]:.0f}×</b> the other large states. '
         f'About <b>{f["weighted_abandon"]:.0%}</b> of callers (<b>{f["abandoned"] / 1e6:,.1f} million</b> calls) hung up '
         f'before reaching anyone.</div>')

# ---------------------------------------------------------------------------
# Page 4: Compare States
# ---------------------------------------------------------------------------
elif page == "Compare States":
    titlebar("Compare States", f"Monthly average wait as reported by each state · {period}")
    names = score.sort_values("state_name")["state_name"].tolist()
    default = [n for n in ["Florida", "Missouri", "Texas"] if n in names]
    picks = st.multiselect("Choose states", names, default=default)
    sub = df[df["state_name"].isin(picks)]
    fig = px.line(sub, x="report_month", y="avg_wait_min", color="state_name", markers=True,
                  color_discrete_sequence=[ACCENT, "#D0839E", "#6B7280", "#3E0A22", "#E4B1C2", "#9CA3AF"],
                  labels={"report_month": "", "avg_wait_min": "Average wait (minutes)", "state_name": ""})
    st.plotly_chart(style_fig(fig, 460), width="stretch", config={"displayModeBar": False})
    st.caption("Wait times are reported in whole minutes (under ~30 seconds shows as 0).")

# ---------------------------------------------------------------------------
# Page 5: About
# ---------------------------------------------------------------------------
else:
    titlebar("About the Data", "Sources, checks and limits")
    a, b = st.columns(2, gap="medium")
    with a:
        card("Data sources",
             '<div class="sub" style="text-align:left;font-size:14px">CMS <i>Medicaid and CHIP CAA Reporting '
             'Metrics</i> (October 2024 release) and the <i>Performance Indicator</i> dataset (March 2026 '
             'release). 17 months, March 2023 – July 2024, 50 states + DC.</div>')
        card("How the numbers were checked",
             '<div class="sub" style="text-align:left;font-size:14px">A Python pipeline cleans the raw files '
             'and logs every problem (417 exceptions). Totals match across Python, SQL and Excel: '
             '<b>867 state-months · 154,681,330 calls · 28,472,216 abandoned calls.</b></div>')
    with b:
        card("Limits to keep in mind",
             '<div class="sub" style="text-align:left;font-size:14px">• States define "call center" '
             'differently, so comparisons show broad patterns, not exact rankings.<br>• South Dakota has no '
             'call center and is excluded.<br>• Waits are whole minutes; 0 means under about 30 seconds.<br>'
             '• Some states changed how they counted calls (RI, HI, AZ); these months are flagged.<br>'
             '• This dashboard shows patterns, not causes.</div>')
        card("Built by",
             '<div class="sub" style="text-align:left;font-size:14px">Juan Villegas · '
             '<a href="https://github.com/villegasjv55/medicaid-access-monitor">GitHub repository</a><br>'
             'Independent portfolio project, not affiliated with CMS or any state.</div>')
