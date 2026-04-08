import requests
import time
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 🏗️ 1. ARCHITECTURAL INIT
load_dotenv()
SPACE_URL = "https://kj2461-trading-env.hf.space"
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip().replace('"', '').replace("'", "")

if not OPENAI_KEY or len(OPENAI_KEY) < 10:
    print("❌ CRITICAL: OPENAI_API_KEY is missing. Update your .env file.")
    exit(1)

client = OpenAI(api_key=OPENAI_KEY)

def get_llm_decision(obs):
    """
    INDUSTRY-STANDARD AGENTIC WRAPPER
    """
    # 🧹 DATA SANITIZATION (Critical for stability)
    pv = round(float(obs.get('port_val', 10000.0)), 2)
    pr = round(float(obs.get('close_price', 0.0)), 2)
    step = int(obs.get('current_step', 20)) - 20
    
    # 🎭 PERSONA-BASED SYSTEM MESSAGE
    messages = [
        {"role": "system", "content": "You are a professional SPY Index Trading Agent. Your goal is to maximize portfolio value while managing risk."},
        {"role": "user", "content": f"MARKET STATE: Min={step}, Portfolio=${pv}, Price=${pr}. Action required: 0 (HOLD), 1 (BUY), 2 (SELL). Respond with ONLY the single digit."}
    ]
    
    # 🔄 RETRY LOOP (Safety net for OpenAI 500s)
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
                max_tokens=3,
                timeout=15.0
            )
            raw_response = response.choices[0].message.content.strip()
            # Robust extraction of the first valid digit
            for char in raw_response:
                if char in "012":
                    return int(char)
            return 0
        except Exception as e:
            if "500" in str(e) and attempt == 0:
                print("⚠️ Server Blip (500). Retrying in 1s...")
                time.sleep(1)
                continue
            print(f"❌ OpenAI Interface Error: {e}")
            return 0

def run_simulation(steps=30):
    print(f"🏁 LAUNCHING INDUSTRY-STANDARD BASELINE...")
    print(f"📡 API ENDPOINT: {SPACE_URL}")
    
    try:
        # WAKE UP & RESET
        print("🔭 Probing Space environment...")
        init_req = requests.post(f"{SPACE_URL}/reset", timeout=15.0)
        obs = init_req.json()
        print(f"✅ CONNECTION ESTABLISHED. Initial State: ${obs.get('port_val', 0):.2f}")
        
        for i in range(steps):
            # 🧠 BRAIN STEP
            action = get_llm_decision(obs)
            action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
            
            # 🏢 ENVIRONMENT STEP
            try:
                resp = requests.post(
                    f"{SPACE_URL}/step", 
                    json={"action": action, "amount": 0.5},
                    timeout=15.0
                )
                obs = resp.json()
                
                cur_min = max(0, obs.get('current_step', 20)-20)
                print(f"[Min {cur_min:02d}] Action: {action_map[action].ljust(4)} | Portfolio: ${obs.get('port_val', 0):.2f}")
                
            except Exception as e:
                print(f"⚠️ Environment Step Failed: {e}")
            
            # ⏲️ PULSE (Ensuring UI refresh sync)
            time.sleep(3)
            
            if obs.get('done', False):
                print("🎬 SESSION COMPLETE (Termination signal received).")
                break
                
    except Exception as e:
        print(f"🛑 CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    run_simulation()
