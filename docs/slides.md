---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    background: #0f172a;
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 32px 52px 24px 52px;
    justify-content: flex-start;
  }
  header {
    color: #38bdf8;
    font-size: 0.68em;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    border-bottom: 2px solid #38bdf8;
    padding-bottom: 6px;
    width: 100%;
  }
  h1 {
    color: #f1f5f9;
    font-size: 1.38em;
    line-height: 1.3;
    margin: 10px 0 12px 0;
    font-weight: 700;
  }
  img {
    border-radius: 8px;
    border: 1px solid #1e293b;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    display: block;
    margin: 0 auto;
  }
  .callout {
    font-size: 0.8em;
    color: #f1f5f9;
    margin: 10px 0 0 0;
    line-height: 1.5;
    background: #1e3a5f;
    border-left: 4px solid #facc15;
    padding: 10px 16px;
    border-radius: 0 6px 6px 0;
  }
  .callout-label {
    color: #facc15;
    font-weight: 800;
    font-size: 0.75em;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: block;
    margin-bottom: 4px;
  }
  .rec-box {
    background: #1e293b;
    border: 1px solid #38bdf8;
    border-radius: 8px;
    padding: 18px 24px;
    margin-top: 12px;
    font-size: 0.9em;
    line-height: 1.6;
    color: #f1f5f9;
  }
  .rec-action {
    color: #38bdf8;
    font-weight: 700;
  }
  .rec-arrow {
    color: #facc15;
    font-weight: 900;
    font-size: 1.1em;
    padding: 0 8px;
  }
  .rec-outcome {
    color: #34d399;
    font-weight: 700;
  }
  .rationale {
    font-size: 0.75em;
    color: #94a3b8;
    margin-top: 10px;
    line-height: 1.55;
    border-left: 3px solid #334155;
    padding-left: 12px;
  }
  footer {
    color: #334155;
    font-size: 0.58em;
  }
---

<!-- _header: "Descriptive Insight" -->
<!-- _footer: "Source: Alpha Vantage daily prices via Snowflake · canon-competitive-intelligence.streamlit.app" -->

# KODK surged +81% while XRX dropped 21% over 90 days — the widest peer spread in the imaging sector

![h:310](dashboard-screenshot.png)

<div class="callout">
  <span class="callout-label">Key Evidence</span>
  KODK (light blue line) diverged sharply from all peers starting in late March, reaching an indexed value of 181 by April 19. XRX (green line) was the only name in sustained decline, ending 21% below the starting baseline.
</div>

---

<!-- _header: "Diagnostic Insight" -->
<!-- _footer: "Source: Alpha Vantage daily prices via Snowflake · canon-competitive-intelligence.streamlit.app" -->

# KODK's volatility was 5x higher than any peer — driven by speculation, not business fundamentals

![h:310](volatility-screenshot.png)

<div class="callout">
  <span class="callout-label">Key Evidence</span>
  The average 30-day price std dev for KODK ($1.02) dwarfs Sony ($0.68), HPQ ($0.45), NINOY ($0.34), and XRX ($0.20). The spike began in late March, coinciding with no major IR announcement — a speculative signal, not an earnings catalyst.
</div>

---

<!-- _header: "Recommendation" -->
<!-- _footer: "Source: Alpha Vantage fundamentals via Snowflake · canon-competitive-intelligence.streamlit.app" -->

# Canon should act on mixed analyst signals in HPQ and XRX before pricing pressure reaches the dealer channel

![h:240](fundamentals-screenshot.png)

<div class="rec-box">
  <span class="rec-action">Monitor HPQ and XRX pricing quarterly</span>
  <span class="rec-arrow">→</span>
  <span class="rec-outcome">Detect enterprise discount pressure 1-2 quarters before it impacts Canon's document solutions revenue</span>
</div>

<p class="rationale">
  HPQ is the only peer with all three analyst signals active (Buy + Hold + Sell), indicating near-term price uncertainty. XRX at $0.24B market cap is structurally distressed and likely to discount aggressively to retain enterprise contracts — a direct threat to Canon's imageRUNNER business.
</p>
