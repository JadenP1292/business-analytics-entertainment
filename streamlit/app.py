import streamlit as st

st.set_page_config(
    page_title="Canon Competitive Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📊 Canon Intelligence")
st.sidebar.caption("Competitive analysis for the imaging & document industry")
st.sidebar.divider()

st.title("Canon Competitive Intelligence Dashboard")
st.markdown("""
Track daily stock performance and analyst signals for Canon's key competitors —
Sony, Nikon, HP, and Xerox — to support strategic pricing and competitive intelligence.

**Use the sidebar to navigate between views.**
""")

st.info("Select a page from the sidebar to begin your analysis.")
