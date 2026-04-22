import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
from utils.snowflake_conn import run_query

st.set_page_config(page_title="Price Trends", page_icon="📈", layout="wide")
st.sidebar.title("📊 Canon Intelligence")
st.sidebar.divider()

TICKERS = ["SONY", "NINOY", "HPQ", "XRX"]
selected = st.sidebar.multiselect("Show companies", TICKERS, default=TICKERS)
days = st.sidebar.selectbox("Time period", [30, 60, 90], index=2, format_func=lambda x: f"Last {x} days")

st.title("📈 Price Trends")
st.caption("How have competitor stock prices moved over time? (Descriptive)")

if not selected:
    st.warning("Select at least one company from the sidebar.")
    st.stop()

tickers_sql = ", ".join(f"'{t}'" for t in selected)

history = run_query(f"""
    select ticker, trade_date, close_price, open_price, high_price, low_price, volume
    from fact_stock_prices
    where trade_date >= dateadd(day, -{days}, current_date)
      and ticker in ({tickers_sql})
    order by ticker, trade_date
""")

fig = px.line(
    history, x="trade_date", y="close_price", color="ticker",
    title=f"Closing Price — Last {days} Days",
    labels={"close_price": "Close Price (USD)", "trade_date": "Date", "ticker": "Company"},
)
fig.update_layout(template="plotly_dark", legend_title="Ticker")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Summary Statistics")
summary = (
    history.groupby("ticker")["close_price"]
    .agg(High="max", Low="min", Average="mean", Latest="last")
    .round(2)
    .reset_index()
    .rename(columns={"ticker": "Ticker"})
)
st.dataframe(summary, use_container_width=True, hide_index=True)
