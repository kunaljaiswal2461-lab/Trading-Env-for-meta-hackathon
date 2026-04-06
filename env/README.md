---
title: Trading Env
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---


A reinforcement learning environment for trading SPY (S&P 500 ETF) using historical price data and technical indicators, deployed as a REST API on Hugging Face Spaces.

## HF Space URL

```
https://your-username-trading-env.hf.space
```

> **Replace `your-username` with your actual HuggingFace username after deployment.**

## Environment Description

The environment simulates trading SPY with a discrete action space:

| Action | Meaning |
|--------|---------|
| `0` | HOLD — do nothing |
| `1` | BUY — buy SPY with all available cash |
| `2` | SELL — sell all SPY holdings |

**Observation space:** 123-dimensional vector  
- 120 market features (20-step window × 6 features: log_return, sma5_dist, sma20_dist, rsi, norm_volume, volatility)  
- 3 portfolio features: cash, holdings, portfolio value

**Reward:** Composite reward — log return + drawdown penalty + differential Sharpe ratio − transaction cost

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns `{"status": "ok"}` |
| `/reset` | POST | Resets environment, returns initial observation |
| `/step` | POST | Takes action `{"action": 0\|1\|2}`, returns next observation |

## Tasks

| Task | Description |
|------|-------------|
| `spy_trading` | Basic trading — 10-step window |
| `risk_aware_trading` | Risk-managed trading — 20-step window |
| `multi_horizon_trading` | Long-horizon trading — 50-step window |

## Setup Instructions

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   API_BASE_URL=https://hf-inference.huggingface.co/v1
   MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
   HF_TOKEN=your_hugging_face_token_here
   INITIAL_CAPITAL=10000
   WINDOW_SIZE=10
   TRANSACTION_COST=0.001
   ```

3. **Start the server:**
   ```bash
   uvicorn env.server.app:app --host 0.0.0.0 --port 8000
   ```

4. **Run inference locally:**
   ```bash
   python inference.py
   ```

### Deployment to HF Spaces

1. **Login to HuggingFace:**
   ```bash
   huggingface-cli login
   ```

2. **Push to HF Spaces:**
   ```bash
   openenv push --space your-username/trading-env
   ```

3. **Wait for build** (10–20 minutes), then verify:
   ```bash
   curl https://your-username-trading-env.hf.space/health
   curl -X POST https://your-username-trading-env.hf.space/reset
   ```

4. **Validate with openenv:**
   ```bash
   openenv validate --url https://your-username-trading-env.hf.space
   ```

5. **Run inference against live Space:**
   ```bash
   SPACE_URL=https://your-username-trading-env.hf.space python inference.py
   ```

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | HuggingFace Inference API base URL |
| `MODEL_NAME` | LLM model name (e.g. `meta-llama/Llama-3.1-8B-Instruct`) |
| `HF_TOKEN` | Your HuggingFace API token (with Write access) |
| `SPACE_URL` | URL of deployed HF Space (for remote inference) |

## Project Structure

```
rl-trading/
├── env/
│   ├── server/
│   │   ├── app.py                  # FastAPI server
│   │   ├── trading_environment.py  # Core RL environment logic
│   │   ├── Dockerfile              # Docker build for HF Spaces
│   │   └── requirements.txt        # Server dependencies
│   ├── models.py                   # Pydantic schemas
│   ├── client.py                   # TradingEnv client
│   ├── reward.py                   # Composite reward calculator
│   └── openenv.yaml                # openenv configuration
├── data/
│   ├── spy_prices.csv              # Preprocessed SPY data
│   ├── fetch_yahoo.py              # Data fetcher
│   └── preprocess.py               # Feature engineering pipeline
├── inference.py                    # Main inference script
├── requirements.txt                # Project dependencies
└── README.md                       # This file
```
