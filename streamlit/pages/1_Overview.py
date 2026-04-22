import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.snowflake_conn import run_query

st.set_page_config(page_title="Overview", page_icon="🏠", layout="wide")
st.sidebar.title("📊 Canon Intelligence")
st.sidebar.divider()
days = st.sidebar.selectbox("Time period", [30, 60, 90], index=2, format_func=lambda x: f"Last {x} days")

st.title("🏠 Overview")
st.caption("Where do Canon's imaging competitors stand today?")

# Latest prices
latest = run_query("""
    select ticker, close_price, trade_date
    from fact_stock_prices
    qualify row_number() over (partition by ticker order by trade_date desc) = 1
""")

# Start prices for period return
start = run_query(f"""
    select ticker, close_price as start_price
    from fact_stock_prices
    where trade_date >= dateadd(day, -{days}, current_date)
    qualify row_number() over (partition by ticker order by trade_date asc) = 1
""")

merged = latest.merge(start, on="ticker", how="left")
merged["return_pct"] = (
    (merged["close_price"] - merged["start_price"]) / merged["start_price"] * 100
).round(2)

# KPI tiles
cols = st.columns(len(merged))
for i, row in merged.iterrows():
    delta = f"{row['return_pct']:+.1f}%" if not pd.isna(row['return_pct']) else "N/A"
    cols[i].metric(
        label=row["ticker"],
        value=f"${row['close_price']:.2f}",
        delta=delta,
    )

st.divider()

# Normalized price chart
history = run_query(f"""
    select ticker, trade_date, close_price
    from fact_stock_prices
    where trade_date >= dateadd(day, -{days}, current_date)
    order by ticker, trade_date
""")

first = history.sort_values("trade_date").groupby("ticker")["close_price"].first()
history["indexed"] = history.apply(
    lambda r: round(r["close_price"] / first[r["ticker"]] * 100, 2), axis=1
)

fig = px.line(
    history, x="trade_date", y="indexed", color="ticker",
    title=f"Indexed Price Performance — Last {days} Days (base = 100)",
    labels={"indexed": "Indexed Price", "trade_date": "Date", "ticker": "Company"},
)
fig.update_layout(template="plotly_dark", legend_title="Ticker")
st.plotly_chart(fig, use_container_width=True)

# Insight callout
if not merged["return_pct"].isna().all():
    best = merged.loc[merged["return_pct"].idxmax()]
    worst = merged.loc[merged["return_pct"].idxmin()]
    st.info(
        f"**Key Insight:** {best['ticker']} led the peer group with "
        f"{best['return_pct']:+.1f}% over the period, "
        f"while {worst['ticker']} lagged at {worst['return_pct']:+.1f}%."
    )
