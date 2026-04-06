from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import uvicorn
import torch
import numpy as np
import traceback
import random

try:
    from env.models import TradingAction, TradingObservation
    from env.agent.policy_network import PolicyNetwork
except ModuleNotFoundError:
    from models import TradingAction, TradingObservation
    from agent.policy_network import PolicyNetwork

app = FastAPI(title="Trading Environment")

# Lazy singleton — initialized on first /reset or /step call, NOT at startup
# This lets /health respond immediately so HF Spaces health check passes
_env = None

def get_env():
    global _env
    if _env is None:
        try:
            from env.server.trading_environment import TradingEnvironment
        except ModuleNotFoundError:
            from server.trading_environment import TradingEnvironment
        _env = TradingEnvironment()
    return _env

# Global trained network
trained_net = None
MODEL_PATH = 'env/checkpoints/best_model.pt' if os.path.exists('env') else 'checkpoints/best_model.pt'

if os.path.exists(MODEL_PATH):
    # Using the correct state_size (123) and action_size (3)
    trained_net = PolicyNetwork(state_size=123, action_size=3)
    # Using agent-style load (which handles dicts)
    ckpt = torch.load(MODEL_PATH, map_location='cpu')
    if isinstance(ckpt, dict) and "online_state_dict" in ckpt:
        trained_net.load_state_dict(ckpt["online_state_dict"])
    else:
        trained_net.load_state_dict(ckpt)
    trained_net.eval()
    print(f'Loaded trained model from {MODEL_PATH}')
else:
    print(f'WARNING: No trained model found at {MODEL_PATH}, /predict will use random')

try:
    from env.server.dashboard import DASHBOARD_HTML
except ModuleNotFoundError:
    from server.dashboard import DASHBOARD_HTML

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML

@app.get("/health")
def health():
    # Responds IMMEDIATELY, no env loading needed
    return {"status": "ok"}

@app.post("/reset", response_model=TradingObservation)
def reset():
    return get_env().reset()

@app.post("/step", response_model=TradingObservation)
def step(action: TradingAction):
    return get_env().step(action)

@app.post("/predict")
async def predict(obs: TradingObservation):
    """Return trained model action for given observation with 15% epsilon."""
    # 15% random exploration so agent still tries BUY/SELL
    if random.random() < 0.15:
        action = int(np.random.randint(3))
        return {
            "action": action, 
            "action_name": ["HOLD", "BUY", "SELL"][action], # Correction: 0=HOLD, 1=BUY, 2=SELL
            "exploration": True
        }
    
    if trained_net is None:
        return {"action": 0, "q_values": [0,0,0], "action_name": "HOLD (MISSING MODEL)"}
    
    try:
        arr = np.array(
            obs.market_features + [obs.port_cash, obs.holdings, obs.port_val],
            dtype=np.float32)
        state_t = torch.FloatTensor(arr).unsqueeze(0)
        with torch.no_grad():
            q = trained_net(state_t)
        action = int(q.argmax(dim=1).item())
        q_vals = q.numpy()[0].tolist()
        return {
            "action": action,
            "q_values": [round(v, 4) for v in q_vals],
            "action_name": ["HOLD", "BUY", "SELL"][action], # Correction: 0=HOLD, 1=BUY, 2=SELL
            "exploration": False
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"action": 0, "error": str(e), "action_name": "HOLD (FAIL)"}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
