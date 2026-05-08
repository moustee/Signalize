"""
╔═══════════════════════════════════════════════════════╗
║        AI FOREX SIGNAL ENGINE  ·  Streamlit App       ║
║   Powered by Claude AI + yfinance + Plotly            ║
╚═══════════════════════════════════════════════════════╝
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
import json
import time
from datetime import datetime, timedelta
from typing import Optional

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Forex Signal Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS  — dark trading-terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #c9d1e0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { font-family: 'Space Mono', monospace !important; }

/* ── Main background ── */
.main .block-container { padding-top: 1rem; background: #080c14; }

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #0d1220;
    border: 1px solid #1e2d45;
    border-radius: 6px;
    padding: 14px 18px;
    box-shadow: 0 0 18px #00d4ff08;
}
div[data-testid="metric-container"] label { color: #4a6fa5 !important; font-size: 0.7rem; letter-spacing: .1em; text-transform: uppercase; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'Space Mono', monospace !important; font-size: 1.4rem; color: #e2e8f4; }

/* ── Signal boxes ── */
.signal-buy {
    background: linear-gradient(135deg, #0a2018 0%, #0d2e1e 100%);
    border: 1px solid #00ff88;
    border-left: 4px solid #00ff88;
    border-radius: 8px;
    padding: 18px 22px;
    box-shadow: 0 0 30px #00ff8820;
}
.signal-sell {
    background: linear-gradient(135deg, #200a0a 0%, #2e0d0d 100%);
    border: 1px solid #ff3366;
    border-left: 4px solid #ff3366;
    border-radius: 8px;
    padding: 18px 22px;
    box-shadow: 0 0 30px #ff336620;
}
.signal-hold {
    background: linear-gradient(135deg, #131a26 0%, #1a2233 100%);
    border: 1px solid #f5a623;
    border-left: 4px solid #f5a623;
    border-radius: 8px;
    padding: 18px 22px;
    box-shadow: 0 0 30px #f5a62320;
}
.signal-label {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: .12em;
}
.signal-buy   .signal-label { color: #00ff88; }
.signal-sell  .signal-label { color: #ff3366; }
.signal-hold  .signal-label { color: #f5a623; }
.signal-reason { font-size: 0.85rem; color: #9aafcc; line-height: 1.65; margin-top: 8px; }
.signal-confidence { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #4a6fa5; margin-top: 6px; letter-spacing: .05em; }

/* ── Section headers ── */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #2d4a6e;
    border-bottom: 1px solid #1a2840;
    padding-bottom: 5px;
    margin-bottom: 14px;
}

/* ── Indicator pills ── */
.indicator-pill {
    display: inline-block;
    background: #111827;
    border: 1px solid #1e3050;
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    margin: 3px;
    color: #7a9cc8;
}
.indicator-pill.bullish { border-color: #00ff8860; color: #00ff88; background: #001a0e; }
.indicator-pill.bearish { border-color: #ff336660; color: #ff3366; background: #1a0008; }
.indicator-pill.neutral { border-color: #f5a62360; color: #f5a623; background: #1a1000; }

/* ── History table ── */
.hist-row {
    display: flex; align-items: center; gap: 14px;
    padding: 9px 14px;
    border-bottom: 1px solid #0e1929;
    font-family: 'Space Mono', monospace; font-size: 0.72rem;
}
.hist-row:hover { background: #0d1a2a; }
.hist-buy  { color: #00ff88; font-weight: 700; }
.hist-sell { color: #ff3366; font-weight: 700; }
.hist-hold { color: #f5a623; font-weight: 700; }
.hist-time { color: #2d4a6e; min-width: 120px; }
.hist-pair { color: #7a9cc8; min-width: 80px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c14; }
::-webkit-scrollbar-thumb { background: #1e3050; border-radius: 2px; }

/* ── Spinner overlay ── */
.stSpinner > div { border-top-color: #00d4ff !important; }

/* ── Button ── */
.stButton > button {
    background: #0d1a2e;
    border: 1px solid #1e3a5f;
    color: #7ab4e8;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: .08em;
    border-radius: 4px;
    transition: all .2s;
}
.stButton > button:hover {
    background: #162540;
    border-color: #2d5a8e;
    color: #a0d4ff;
    box-shadow: 0 0 12px #00d4ff15;
}

/* ── Selectbox / sliders ── */
.stSelectbox label, .stSlider label { color: #4a6fa5; font-size: 0.72rem; letter-spacing: .08em; }
div[data-baseweb="select"] > div { background: #0d1220 !important; border-color: #1e2d45 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "USD/CHF": "CHF=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
}
TIMEFRAMES = {
    "1 Hour":  ("1h",  "5d"),
    "4 Hours": ("1h",  "10d"),
    "Daily":   ("1d",  "60d"),
    "Weekly":  ("1wk", "1y"),
}
CHART_BG = "#080c14"
GRID_COLOR = "#0e1929"


# ─────────────────────────────────────────────
# TECHNICAL ANALYSIS
# ─────────────────────────────────────────────
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]

    # ── EMAs
    df["EMA_9"]  = close.ewm(span=9,  adjust=False).mean()
    df["EMA_21"] = close.ewm(span=21, adjust=False).mean()
    df["EMA_50"] = close.ewm(span=50, adjust=False).mean()

    # ── RSI (14)
    delta = close.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ── MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]

    # ── Bollinger Bands (20, 2)
    sma20    = close.rolling(20).mean()
    std20    = close.rolling(20).std()
    df["BB_Upper"]  = sma20 + 2 * std20
    df["BB_Lower"]  = sma20 - 2 * std20
    df["BB_Middle"] = sma20

    # ── ATR (14)
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # ── Stochastic %K, %D (14, 3)
    lo14 = low.rolling(14).min()
    hi14 = high.rolling(14).max()
    df["Stoch_K"] = 100 * (close - lo14) / (hi14 - lo14).replace(0, np.nan)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # ── ADX (14)
    plus_dm  = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    mask = plus_dm < minus_dm; plus_dm[mask] = 0
    mask = minus_dm < plus_dm.shift(); minus_dm[mask] = 0
    atr14      = df["ATR"]
    plus_di    = 100 * plus_dm.ewm(com=13, adjust=False).mean() / atr14.replace(0, np.nan)
    minus_di   = 100 * minus_dm.ewm(com=13, adjust=False).mean() / atr14.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["ADX"]      = dx.ewm(com=13, adjust=False).mean()
    df["Plus_DI"]  = plus_di
    df["Minus_DI"] = minus_di

    return df.dropna()


def indicator_summary(df: pd.DataFrame) -> dict:
    """Return latest indicator snapshot as a clean dict for the AI."""
    row = df.iloc[-1]
    prev = df.iloc[-2]
    return {
        "price":       round(float(row["Close"]), 5),
        "open":        round(float(row["Open"]), 5),
        "high_1bar":   round(float(row["High"]), 5),
        "low_1bar":    round(float(row["Low"]), 5),
        "ema_9":       round(float(row["EMA_9"]), 5),
        "ema_21":      round(float(row["EMA_21"]), 5),
        "ema_50":      round(float(row["EMA_50"]), 5),
        "rsi_14":      round(float(row["RSI"]), 2),
        "macd":        round(float(row["MACD"]), 6),
        "macd_signal": round(float(row["MACD_Signal"]), 6),
        "macd_hist":   round(float(row["MACD_Hist"]), 6),
        "bb_upper":    round(float(row["BB_Upper"]), 5),
        "bb_lower":    round(float(row["BB_Lower"]), 5),
        "atr_14":      round(float(row["ATR"]), 6),
        "stoch_k":     round(float(row["Stoch_K"]), 2),
        "stoch_d":     round(float(row["Stoch_D"]), 2),
        "adx":         round(float(row["ADX"]), 2),
        "plus_di":     round(float(row["Plus_DI"]), 2),
        "minus_di":    round(float(row["Minus_DI"]), 2),
        "prev_close":  round(float(prev["Close"]), 5),
        "price_change_pct": round((float(row["Close"]) - float(prev["Close"])) / float(prev["Close"]) * 100, 4),
    }


# ─────────────────────────────────────────────
# AI SIGNAL GENERATION
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior algorithmic forex trading analyst with 15+ years of experience.
You analyse technical indicators and generate structured trading signals.

Given indicator data, respond ONLY with a valid JSON object (no markdown, no extra text):
{
  "signal":      "BUY" | "SELL" | "HOLD",
  "confidence":  <integer 0–100>,
  "entry_price": <float | null>,
  "stop_loss":   <float | null>,
  "take_profit": <float | null>,
  "risk_reward": <float | null>,
  "timeframe_bias": "BULLISH" | "BEARISH" | "NEUTRAL",
  "key_levels": {
    "support": [<float>, ...],
    "resistance": [<float>, ...]
  },
  "indicator_signals": {
    "trend":     "BULLISH" | "BEARISH" | "NEUTRAL",
    "momentum":  "BULLISH" | "BEARISH" | "NEUTRAL",
    "volatility":"HIGH" | "MEDIUM" | "LOW",
    "strength":  "STRONG" | "MODERATE" | "WEAK"
  },
  "reasoning": "<2–4 sentence concise analysis>",
  "risks": "<1–2 sentence key risk factors>"
}"""


def get_ai_signal(pair: str, timeframe: str, indicators: dict, api_key: str) -> Optional[dict]:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        user_msg = (
            f"Currency pair: {pair} | Timeframe: {timeframe}\n"
            f"Indicator snapshot:\n{json.dumps(indicators, indent=2)}\n\n"
            "Generate a precise trading signal."
        )
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=900,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        # Strip possible markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        st.error(f"AI signal error: {e}")
        return None


# ─────────────────────────────────────────────
# CHART BUILDER
# ─────────────────────────────────────────────
def build_chart(df: pd.DataFrame, pair: str, signal: Optional[dict]) -> go.Figure:
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.56, 0.22, 0.22],
        vertical_spacing=0.03,
        subplot_titles=("", "RSI (14)", "MACD"),
    )

    # ── Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_fillcolor="#00ff88", increasing_line_color="#00ff88",
        decreasing_fillcolor="#ff3366", decreasing_line_color="#ff3366",
        line_width=1, name="Price",
    ), row=1, col=1)

    # ── EMAs
    for span, color, width in [(9, "#00d4ff", 1.2), (21, "#7a5ef8", 1.2), (50, "#f5a623", 1.4)]:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[f"EMA_{span}"], mode="lines",
            line=dict(color=color, width=width, dash="solid"),
            name=f"EMA {span}", opacity=0.8,
        ), row=1, col=1)

    # ── Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Upper"], mode="lines",
        line=dict(color="#2d4a6e", width=1, dash="dot"),
        name="BB Upper", opacity=0.6,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Lower"], mode="lines",
        line=dict(color="#2d4a6e", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(45,74,110,0.07)",
        name="BB Lower", opacity=0.6,
    ), row=1, col=1)

    # ── Signal entry line
    if signal and signal.get("entry_price"):
        ep = signal["entry_price"]
        fig.add_hline(y=ep, line_color="#00d4ff", line_width=1.2,
                      line_dash="dash", row=1, col=1, opacity=0.7,
                      annotation_text=f"Entry {ep:.5f}",
                      annotation_font_color="#00d4ff", annotation_font_size=10)
    if signal and signal.get("stop_loss"):
        sl = signal["stop_loss"]
        fig.add_hline(y=sl, line_color="#ff3366", line_width=1,
                      line_dash="dot", row=1, col=1, opacity=0.7,
                      annotation_text=f"SL {sl:.5f}",
                      annotation_font_color="#ff3366", annotation_font_size=10)
    if signal and signal.get("take_profit"):
        tp = signal["take_profit"]
        fig.add_hline(y=tp, line_color="#00ff88", line_width=1,
                      line_dash="dot", row=1, col=1, opacity=0.7,
                      annotation_text=f"TP {tp:.5f}",
                      annotation_font_color="#00ff88", annotation_font_size=10)

    # ── RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"], mode="lines",
        line=dict(color="#00d4ff", width=1.5), name="RSI",
    ), row=2, col=1)
    for lvl, col in [(70, "#ff336640"), (30, "#00ff8840")]:
        fig.add_hline(y=lvl, line_color=col, line_width=1,
                      line_dash="dot", row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ff336608", line_width=0, row=2, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="#00ff8808", line_width=0, row=2, col=1)

    # ── MACD
    colors = ["#00ff88" if v >= 0 else "#ff3366" for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(
        x=df.index, y=df["MACD_Hist"],
        marker_color=colors, name="MACD Hist", opacity=0.7,
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"], mode="lines",
        line=dict(color="#7a5ef8", width=1.4), name="MACD",
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_Signal"], mode="lines",
        line=dict(color="#f5a623", width=1.4), name="Signal",
    ), row=3, col=1)

    # ── Layout
    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        margin=dict(l=0, r=0, t=28, b=0),
        font=dict(family="Space Mono", color="#4a6fa5", size=10),
        legend=dict(
            bgcolor="#0d1220", bordercolor="#1e2d45",
            borderwidth=1, font_size=9,
            orientation="h", y=1.02, x=0,
        ),
        xaxis_rangeslider_visible=False,
        height=580,
    )
    for i in range(1, 4):
        fig.update_xaxes(
            gridcolor=GRID_COLOR, zeroline=False,
            tickfont=dict(size=9), showgrid=True,
            row=i, col=1,
        )
        fig.update_yaxes(
            gridcolor=GRID_COLOR, zeroline=False,
            tickfont=dict(size=9), showgrid=True,
            row=i, col=1,
        )
    return fig


# ─────────────────────────────────────────────
# SIGNAL HISTORY (session state)
# ─────────────────────────────────────────────
def add_to_history(pair: str, tf: str, signal: dict):
    if "signal_history" not in st.session_state:
        st.session_state.signal_history = []
    st.session_state.signal_history.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "pair": pair,
        "timeframe": tf,
        "signal": signal.get("signal", "?"),
        "confidence": signal.get("confidence", 0),
        "entry": signal.get("entry_price"),
        "rr": signal.get("risk_reward"),
    })
    if len(st.session_state.signal_history) > 20:
        st.session_state.signal_history = st.session_state.signal_history[:20]


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 18px 0 12px;'>
      <div style='font-family:Space Mono; font-size:1.05rem; color:#00d4ff; letter-spacing:.15em;'>⚡ FOREX</div>
      <div style='font-family:Syne; font-size:1.5rem; font-weight:800; color:#e2e8f4; letter-spacing:.05em;'>SIGNAL ENGINE</div>
      <div style='font-family:Space Mono; font-size:0.58rem; color:#2d4a6e; letter-spacing:.2em; margin-top:2px;'>POWERED BY CLAUDE AI</div>
    </div>
    <hr style='border-color:#1a2840; margin:0 0 18px;'>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-title">ANTHROPIC API KEY</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key", type="password", placeholder="sk-ant-…",
        help="Get your key at console.anthropic.com",
        label_visibility="collapsed",
    )

    st.markdown('<br><p class="section-title">INSTRUMENT</p>', unsafe_allow_html=True)
    pair_label = st.selectbox("Currency Pair", list(PAIRS.keys()), label_visibility="collapsed")
    ticker = PAIRS[pair_label]

    st.markdown('<br><p class="section-title">TIMEFRAME</p>', unsafe_allow_html=True)
    tf_label = st.selectbox("Timeframe", list(TIMEFRAMES.keys()), label_visibility="collapsed")
    tf_interval, tf_period = TIMEFRAMES[tf_label]

    st.markdown('<br><p class="section-title">AUTO-REFRESH</p>', unsafe_allow_html=True)
    auto_refresh = st.toggle("Enable Auto-Refresh", value=False)
    if auto_refresh:
        refresh_mins = st.slider("Interval (minutes)", 1, 30, 5)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("⚡  GENERATE SIGNAL", use_container_width=True)

    st.markdown("""
    <br>
    <div style='font-family:Space Mono; font-size:0.6rem; color:#1a2840; text-align:center; line-height:1.7;'>
      ⚠ For educational use only.<br>
      Not financial advice.<br>
      Trade at your own risk.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AUTO-REFRESH LOGIC
# ─────────────────────────────────────────────
if auto_refresh:
    last_refresh = st.session_state.get("last_refresh", 0)
    if time.time() - last_refresh > refresh_mins * 60:
        run_btn = True
        st.session_state["last_refresh"] = time.time()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:baseline; gap:14px; margin-bottom:4px;'>
  <span style='font-family:Syne; font-size:1.8rem; font-weight:800; color:#e2e8f4;'>{pair_label}</span>
  <span style='font-family:Space Mono; font-size:0.7rem; color:#2d4a6e; letter-spacing:.15em;'>{tf_label.upper()} · LIVE DATA</span>
  <span style='font-family:Space Mono; font-size:0.65rem; color:#1a2840; margin-left:auto;'>{datetime.now().strftime("%Y-%m-%d  %H:%M:%S")}</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(ticker: str, interval: str, period: str) -> pd.DataFrame:
    df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


with st.spinner("Fetching live market data…"):
    df_raw = fetch_data(ticker, tf_interval, tf_period)

if df_raw.empty:
    st.error("⚠ Could not fetch data for this pair. Check your connection or try another pair.")
    st.stop()

df = compute_indicators(df_raw.copy())
if df.empty or len(df) < 30:
    st.error("⚠ Insufficient data to compute all indicators. Try a longer timeframe.")
    st.stop()

indic = indicator_summary(df)
last_price  = indic["price"]
prev_price  = indic["prev_close"]
pct_change  = indic["price_change_pct"]
price_color = "#00ff88" if pct_change >= 0 else "#ff3366"
arrow       = "▲" if pct_change >= 0 else "▼"


# ─────────────────────────────────────────────
# METRICS ROW
# ─────────────────────────────────────────────
m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    st.metric("Last Price",  f"{last_price:.5f}", f"{arrow} {abs(pct_change):.4f}%")
with m2:
    st.metric("RSI (14)",    f"{indic['rsi_14']:.1f}", 
              "Overbought" if indic['rsi_14'] > 70 else ("Oversold" if indic['rsi_14'] < 30 else "Neutral"))
with m3:
    st.metric("ATR (14)",    f"{indic['atr_14']:.5f}")
with m4:
    st.metric("ADX (14)",    f"{indic['adx']:.1f}",
              "Strong" if indic['adx'] > 25 else "Weak")
with m5:
    st.metric("Stoch %K",    f"{indic['stoch_k']:.1f}")
with m6:
    st.metric("EMA 9/21",
              "↑ Bullish" if indic["ema_9"] > indic["ema_21"] else "↓ Bearish")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LAYOUT: Chart | Signal
# ─────────────────────────────────────────────
col_chart, col_signal = st.columns([2.4, 1], gap="medium")

signal_result = st.session_state.get("signal_result")
last_pair = st.session_state.get("last_pair")
last_tf   = st.session_state.get("last_tf")

with col_chart:
    st.markdown('<p class="section-title">PRICE CHART  ·  TECHNICAL INDICATORS</p>', unsafe_allow_html=True)
    chart_placeholder = st.empty()
    with chart_placeholder:
        fig = build_chart(df, pair_label,
                          signal_result if (last_pair == pair_label and last_tf == tf_label) else None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_signal:
    st.markdown('<p class="section-title">AI TRADING SIGNAL</p>', unsafe_allow_html=True)

    if run_btn:
        if not api_key:
            st.warning("⚠ Enter your Anthropic API key in the sidebar first.")
        else:
            with st.spinner("Claude is analysing the market…"):
                signal_result = get_ai_signal(pair_label, tf_label, indic, api_key)
            if signal_result:
                st.session_state["signal_result"] = signal_result
                st.session_state["last_pair"]     = pair_label
                st.session_state["last_tf"]       = tf_label
                add_to_history(pair_label, tf_label, signal_result)
                # Refresh chart with levels
                with chart_placeholder:
                    fig = build_chart(df, pair_label, signal_result)
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": False})

    if signal_result and last_pair == pair_label and last_tf == tf_label:
        sig  = signal_result.get("signal", "HOLD")
        conf = signal_result.get("confidence", 0)
        css  = {"BUY": "signal-buy", "SELL": "signal-sell"}.get(sig, "signal-hold")
        emoji = {"BUY": "🟢", "SELL": "🔴"}.get(sig, "🟡")

        st.markdown(f"""
        <div class="{css}">
          <div class="signal-label">{emoji} {sig}</div>
          <div class="signal-confidence">CONFIDENCE: {conf}%</div>
          <div class="signal-reason">{signal_result.get('reasoning', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Trade levels
        st.markdown('<p class="section-title">TRADE LEVELS</p>', unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)
        ep = signal_result.get("entry_price")
        sl = signal_result.get("stop_loss")
        tp = signal_result.get("take_profit")
        rr = signal_result.get("risk_reward")
        with lc1:
            st.metric("Entry",       f"{ep:.5f}" if ep else "—")
            st.metric("Stop Loss",   f"{sl:.5f}" if sl else "—")
        with lc2:
            st.metric("Take Profit", f"{tp:.5f}" if tp else "—")
            st.metric("Risk/Reward", f"1:{rr:.1f}" if rr else "—")

        # ── Indicator signals
        st.markdown('<br><p class="section-title">INDICATOR BREAKDOWN</p>', unsafe_allow_html=True)
        i_sig = signal_result.get("indicator_signals", {})
        pills_html = ""
        for label, val in i_sig.items():
            cls = "bullish" if val in ("BULLISH","STRONG","HIGH") else \
                  "bearish" if val in ("BEARISH","WEAK") else "neutral"
            pills_html += f'<span class="indicator-pill {cls}">{label.upper()}: {val}</span>'
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)

        # ── Timeframe bias
        bias = signal_result.get("timeframe_bias", "NEUTRAL")
        b_cls = "bullish" if bias == "BULLISH" else ("bearish" if bias == "BEARISH" else "neutral")
        st.markdown(f'<br><span class="indicator-pill {b_cls}">TIMEFRAME BIAS: {bias}</span>', unsafe_allow_html=True)

        # ── Risks
        risks = signal_result.get("risks")
        if risks:
            st.markdown(f"""
            <div style='margin-top:14px; background:#0d1220; border:1px solid #1e2d45;
                        border-radius:6px; padding:12px 14px;
                        font-size:0.78rem; color:#4a6fa5; line-height:1.6;'>
              ⚠&nbsp; <b style='color:#2d4a6e;'>RISKS</b><br>{risks}
            </div>
            """, unsafe_allow_html=True)

        # ── Key levels
        kl = signal_result.get("key_levels", {})
        sup = kl.get("support", [])
        res = kl.get("resistance", [])
        if sup or res:
            st.markdown('<br><p class="section-title">KEY LEVELS</p>', unsafe_allow_html=True)
            kc1, kc2 = st.columns(2)
            with kc1:
                st.markdown("**Support**")
                for lvl in sup[:3]:
                    st.markdown(f'<span class="indicator-pill bullish">{lvl:.5f}</span>', unsafe_allow_html=True)
            with kc2:
                st.markdown("**Resistance**")
                for lvl in res[:3]:
                    st.markdown(f'<span class="indicator-pill bearish">{lvl:.5f}</span>', unsafe_allow_html=True)

    elif not run_btn:
        st.markdown("""
        <div style='background:#0d1220; border:1px solid #1a2840; border-radius:8px;
                    padding:32px 22px; text-align:center; color:#2d4a6e;'>
          <div style='font-size:2.2rem; margin-bottom:10px; opacity:.5;'>⚡</div>
          <div style='font-family:Space Mono; font-size:0.72rem; letter-spacing:.12em;'>
            Enter your API key &amp; click<br><b style='color:#4a6fa5;'>GENERATE SIGNAL</b>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INDICATORS TABLE
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊  Detailed Indicator Values", expanded=False):
    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.markdown("**Trend**")
        st.metric("EMA 9",  f"{indic['ema_9']:.5f}")
        st.metric("EMA 21", f"{indic['ema_21']:.5f}")
        st.metric("EMA 50", f"{indic['ema_50']:.5f}")
    with ic2:
        st.markdown("**Momentum**")
        st.metric("RSI 14",   f"{indic['rsi_14']:.2f}")
        st.metric("Stoch %K", f"{indic['stoch_k']:.2f}")
        st.metric("Stoch %D", f"{indic['stoch_d']:.2f}")
    with ic3:
        st.markdown("**MACD**")
        st.metric("MACD",        f"{indic['macd']:.6f}")
        st.metric("Signal Line", f"{indic['macd_signal']:.6f}")
        st.metric("Histogram",   f"{indic['macd_hist']:.6f}")
    with ic4:
        st.markdown("**Volatility / Trend Strength**")
        st.metric("ATR 14",   f"{indic['atr_14']:.6f}")
        st.metric("ADX 14",   f"{indic['adx']:.2f}")
        st.metric("+DI / -DI", f"{indic['plus_di']:.2f} / {indic['minus_di']:.2f}")


# ─────────────────────────────────────────────
# SIGNAL HISTORY
# ─────────────────────────────────────────────
history = st.session_state.get("signal_history", [])
if history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">SIGNAL HISTORY  (LAST 20)</p>', unsafe_allow_html=True)
    rows_html = ""
    for h in history:
        s = h["signal"]
        cls = {"BUY": "hist-buy", "SELL": "hist-sell"}.get(s, "hist-hold")
        ep  = f"{h['entry']:.5f}" if h.get("entry") else "—"
        rr  = f"1:{h['rr']:.1f}" if h.get("rr") else "—"
        rows_html += f"""
        <div class="hist-row">
          <span class="hist-time">{h['time']}</span>
          <span class="hist-pair">{h['pair']}</span>
          <span style='color:#2d4a6e; font-size:0.68rem;'>{h['timeframe']}</span>
          <span class="{cls}">{s}</span>
          <span style='color:#4a6fa5;'>{h['confidence']}%</span>
          <span style='color:#2d4a6e;'>Entry {ep}</span>
          <span style='color:#2d4a6e;'>R/R {rr}</span>
        </div>"""
    st.markdown(
        f'<div style="background:#0d1220; border:1px solid #1e2d45; border-radius:8px; overflow:hidden;">{rows_html}</div>',
        unsafe_allow_html=True,
    )
