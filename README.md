# ⚡ AI Forex Signal Engine

A production-grade live forex trading signal dashboard powered by **Claude AI** (Anthropic), 
built with Streamlit, yfinance, and Plotly.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **10 Currency Pairs** | EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, NZD/USD, EUR/GBP, EUR/JPY, GBP/JPY |
| **4 Timeframes** | 1H · 4H · Daily · Weekly |
| **9 Indicators** | EMA 9/21/50, RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX |
| **AI Signal** | BUY / SELL / HOLD with confidence score, entry, SL, TP, R/R |
| **Key Levels** | AI-identified support & resistance zones |
| **Signal History** | Last 20 signals logged in-session |
| **Auto-Refresh** | 1–30 min configurable interval |
| **Interactive Chart** | Candlestick + indicators + trade levels overlay |

---

## 📦 Setup

### 1. Clone or download
```bash
mkdir forex-signal-engine && cd forex-signal-engine
# Place app.py and requirements.txt here
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get API Key
Go to [console.anthropic.com](https://console.anthropic.com) → API Keys → Create key.

### 5. Run locally
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploy to Streamlit Cloud (free)

1. Push your project to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo and `app.py` as the entrypoint
4. *(Optional)* Add your API key as a **Secret**:
   - In Streamlit Cloud dashboard → ⚙️ Settings → **Secrets**
   - Add: `ANTHROPIC_API_KEY = "sk-ant-xxxxx"`
   - Then in `app.py` change the API key input to:  
     `api_key = st.secrets.get("ANTHROPIC_API_KEY", "")`

---

## 🐳 Deploy with Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t forex-signals .
docker run -p 8501:8501 forex-signals
```

---

## 🧠 How the AI Signal Works

1. **Data Fetch** — yfinance pulls OHLCV candles for the selected pair/timeframe
2. **Indicators** — 9 technical indicators are computed with pandas/numpy
3. **Snapshot** — A structured JSON of the latest indicator values is built
4. **Claude AI** — The snapshot is sent to `claude-sonnet-4-20250514` with a
   specialized system prompt instructing it to respond with a strict JSON signal
5. **Rendering** — The response is parsed and rendered as an interactive dashboard

---

## ⚠️ Disclaimer

This application is for **educational and research purposes only**.  
It does **not** constitute financial advice.  
Forex trading involves significant risk. **Trade at your own risk.**

---

## 📁 File Structure

```
forex-signal-engine/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```
