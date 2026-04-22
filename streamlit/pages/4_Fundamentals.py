import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.snowflake_conn import run_query

st.set_page_config(page_title="Fundamentals", page_icon="🏦", layout="wide")
st.sidebar.title("📊 Canon Intelligence")
st.sidebar.divider()

metric_options = {
    "Market Cap (B)": "market_capitalization",
    "P/E Ratio": "pe_ratio",
    "Analyst Target Price": "analyst_target_price",
    "52-Week High": "week_52_high",
    "52-Week Low": "week_52_low",
}
selected_metric_label = st.sidebar.selectbox("Highlight metric", list(metric_options.keys()))
selected_metric = metric_options[selected_metric_label]

st.title("🏦 Fundamentals")
st.caption("What do analyst signals say about each competitor? (Diagnostic)")

snapshot = run_query("""
    select ticker, market_capitalization, pe_ratio, forward_pe,
           week_52_high, week_52_low, analyst_target_price,
           analyst_rating_buy, analyst_rating_hold, analyst_rating_sell,
           snapshot_date
    from fact_company_snapshot
    qualify row_number() over (partition by ticker order by snapshot_date desc) = 1
""")

if snapshot.empty:
    st.warning("No fundamentals data available yet. Run the extraction pipeline first.")
    st.stop()

snapshot["market_capitalization"] = (snapshot["market_capitalization"] / 1e9).round(2)

ratings = snapshot[["ticker", "analyst_rating_buy", "analyst_rating_hold", "analyst_rating_sell"]].copy()
ratings = ratings.rename(columns={
    "analyst_rating_buy": "Buy",
    "analyst_rating_hold": "Hold",
    "analyst_rating_sell": "Sell",
})
ratings_long = ratings.melt(id_vars="ticker", var_name="Rating", value_name="Count")
ratings_long = ratings_long.dropna(subset=["Count"])

fig_ratings = px.bar(
    ratings_long, x="ticker", y="Count", color="Rating",
    barmode="stack",
    color_discrete_map={"Buy": "#34d399", "Hold": "#fbbf24", "Sell": "#f87171"},
    title="Analyst Ratings Breakdown",
    labels={"ticker": "Company", "Count": "# Analysts"},
)
fig_ratings.update_layout(template="plotly_dark")
st.plotly_chart(fig_ratings, use_container_width=True)

metric_data = snapshot[["ticker", selected_metric]].dropna()
fig_metric = px.bar(
    metric_data.sort_values(selected_metric, ascending=False),
    x="ticker", y=selected_metric, color="ticker",
    title=f"{selected_metric_label} by Company",
    labels={"ticker": "Company", selected_metric: selected_metric_label},
)
fig_metric.update_layout(template="plotly_dark", showlegend=False)
st.plotly_chart(fig_metric, use_container_width=True)

display_cols = {
    "ticker": "Ticker",
    "market_capitalization": "Market Cap ($B)",
    "pe_ratio": "P/E Ratio",
    "analyst_target_price": "Analyst Target",
    "week_52_high": "52W High",
    "week_52_low": "52W Low",
}
table = snapshot[list(display_cols.keys())].rename(columns=display_cols)
st.subheader("Full Metrics Table")
st.dataframe(table.round(2), use_container_width=True, hide_index=True)
