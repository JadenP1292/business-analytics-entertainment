import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.snowflake_conn import run_query

st.set_page_config(page_title="Volatility", page_icon="⚡", layout="wide")
st.sidebar.title("📊 Canon Intelligence")
st.sidebar.divider()

window = st.sidebar.select_slider("Rolling window (days)", options=[7, 14, 30], value=30)
days = st.sidebar.selectbox("History period", [60, 90], index=1, format_func=lambda x: f"Last {x} days")

st.title("⚡ Volatility & Risk")
st.caption("Why did some competitors move more than others? (Diagnostic)")

history = run_query(f"""
    select ticker, trade_date, close_price
    from fact_stock_prices
    where trade_date >= dateadd(day, -{days}, current_date)
    order by ticker, trade_date
""")

history["trade_date"] = pd.to_datetime(history["trade_date"])
history = history.sort_values(["ticker", "trade_date"])
history["rolling_vol"] = (
    history.groupby("ticker")["close_price"]
    .transform(lambda x: x.rolling(window).std())
)

fig_line = px.line(
    history.dropna(subset=["rolling_vol"]),
    x="trade_date", y="rolling_vol", color="ticker",
    title=f"{window}-Day Rolling Price Volatility (Std Dev)",
    labels={"rolling_vol": "Price Std Dev (USD)", "trade_date": "Date", "ticker": "Company"},
)
fig_line.update_layout(template="plotly_dark")
st.plotly_chart(fig_line, use_container_width=True)

avg_vol = (
    history.groupby("ticker")["rolling_vol"]
    .mean().round(4).reset_index()
    .rename(columns={"rolling_vol": "avg_volatility"})
    .sort_values("avg_volatility", ascending=False)
)

fig_bar = px.bar(
    avg_vol, x="ticker", y="avg_volatility", color="ticker",
    title=f"Average {window}-Day Volatility by Company",
    labels={"avg_volatility": "Avg Price Std Dev (USD)", "ticker": "Company"},
)
fig_bar.update_layout(template="plotly_dark", showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)

most_volatile = avg_vol.iloc[0]
least_volatile = avg_vol.iloc[-1]
st.info(
    f"**Diagnostic Insight:** {most_volatile['ticker']} showed the highest average volatility "
    f"(±${most_volatile['avg_volatility']:.2f}) over the period — "
    f"{(most_volatile['avg_volatility'] / least_volatile['avg_volatility']):.1f}× "
    f"more than {least_volatile['ticker']}. "
    f"Higher volatility signals greater market uncertainty around that company's outlook."
)
