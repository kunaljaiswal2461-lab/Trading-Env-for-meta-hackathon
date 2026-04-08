from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gradio as gr
import pandas as pd
import os
from models import TradingAction, TradingObservation

# 1. Initialize FastAPI
app = FastAPI(title="SPY RL Environment API")

# 🌍 GLOBAL CORS MIDDLEWARE (The 'VIP Pass' for Judges)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Accept connections from ANY laptop in the world
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singleton
_env = None
def get_env():
    global _env
    if _env is None:
        from server.trading_environment import TradingEnvironment
        _env = TradingEnvironment()
    return _env

# --- MIRROR REDIRECTS ---
@app.get("/web")
def web_redirect():
    return RedirectResponse(url="/")

@app.get("/health")
def health():
    return {"status": "ok"}

# --- API ROUTES ---
@app.post("/reset", response_model=TradingObservation)
def reset():
    return get_env().reset()

@app.post("/step", response_model=TradingObservation)
def step(action: TradingAction):
    return get_env().step(action)

# --- PASSIVE MONITOR LOGIC ---
_pv_data = pd.DataFrame({"Minute": [0], "Portfolio Value": [10000.0]})
_price_data = pd.DataFrame({"Minute": [0], "SPY Price": [100.0]})

def get_live_state():
    """Reads current state and updates history for the charts."""
    env = get_env()
    obs = env._get_obs(reward=0, done=False)
    
    global _pv_data, _price_data
    # Safe minute calculation
    cur_min = max(0, obs.current_step - 20)
    
    if obs.current_step <= 21: # RESET
        _pv_data = pd.DataFrame({"Minute": [0], "Portfolio Value": [obs.port_val]})
        _price_data = pd.DataFrame({"Minute": [0], "SPY Price": [obs.close_price]})
    else:
        if cur_min > _pv_data["Minute"].max():
            _pv_data = pd.concat([_pv_data, pd.DataFrame({"Minute": [cur_min], "Portfolio Value": [obs.port_val]})], ignore_index=True)
            _price_data = pd.concat([_price_data, pd.DataFrame({"Minute": [cur_min], "SPY Price": [obs.close_price]})], ignore_index=True)

    return [
        f"${obs.port_val:.2f}", f"${obs.close_price:.2f}", f"{obs.holdings:.3f} SPY", f"${obs.port_cash:.2f}", 
        f"{obs.reward:.4f}", f"Minute {cur_min}", _pv_data, _price_data
    ]

def manual_step(action_idx, amount_pct):
    amount = float(amount_pct) / 100.0
    get_env().step(TradingAction(action=action_idx, amount=amount))
    return get_live_state()

def manual_reset():
    get_env().reset()
    return get_live_state()

# --- THE UI MASTERPIECE ---
with gr.Blocks(theme=gr.themes.Soft(), title="SPY RL Trading Hub") as demo:
    gr.Markdown("# 🛰️ SPY Trading Environment\n*Live session monitoring for Reinforcement Learning agents.*")
    
    with gr.Row():
        with gr.Column(scale=1):
            perf_chart = gr.LinePlot(
                value=_pv_data, x="Minute", y="Portfolio Value", 
                title="📈 Session Portfolio Growth", height=380,
                y_lim=None, overlay_point=True, tooltip=["Minute", "Portfolio Value"]
            )
        with gr.Column(scale=1):
            price_chart = gr.LinePlot(
                value=_price_data, x="Minute", y="SPY Price", 
                title="📊 SPY Live Price Feed", height=380,
                color_line="orange",
                y_lim=None, overlay_point=True, tooltip=["Minute", "SPY Price"]
            )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📡 Terminal Feed")
            with gr.Row():
                v1 = gr.Textbox(label="Account Value", interactive=False)
                v1_price = gr.Textbox(label="Last Price", interactive=False)
            with gr.Row():
                v2 = gr.Textbox(label="SPY Position", interactive=False)
                v3 = gr.Textbox(label="Cash on Hand", interactive=False)
            with gr.Row():
                v4 = gr.Textbox(label="Latest P/L Reward", interactive=False)
                v5 = gr.Textbox(label="Session Duration", interactive=False)
                
        with gr.Column(scale=1):
            with gr.Accordion("🛠️ Manual Control Pad", open=True):
                gr.Markdown("Execute manual overrides or advance the session time.")
                amount_slider = gr.Slider(1, 100, step=1, value=100, label="Trade Order Size (%)")
                with gr.Row():
                    b1 = gr.Button("⏩ HOLD / NEXT MINUTE", variant="secondary")
                    b2 = gr.Button("🟢 BUY SPY", variant="primary")
                    b3 = gr.Button("🔴 SELL SPY", variant="stop")
                b0 = gr.Button("🔄 FULL SESSION RESET", variant="secondary")

    # The Live Heartbeat
    timer = gr.Timer(2)
    timer.tick(get_live_state, outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])
    
    # Event Handlers
    b1.click(manual_step, inputs=[gr.Number(0, visible=False), amount_slider], outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])
    b2.click(manual_step, inputs=[gr.Number(1, visible=False), amount_slider], outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])
    b3.click(manual_step, inputs=[gr.Number(2, visible=False), amount_slider], outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])
    b0.click(manual_reset, outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])
    
    demo.load(get_live_state, outputs=[v1, v1_price, v2, v3, v4, v5, perf_chart, price_chart])

app = gr.mount_gradio_app(app, demo, path="/")

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
