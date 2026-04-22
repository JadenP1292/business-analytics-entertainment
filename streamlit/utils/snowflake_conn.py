import streamlit as st
import snowflake.connector
import pandas as pd


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema="MART",
    )


@st.cache_data(ttl=3600)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query)
        cols = [desc[0].lower() for desc in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)
