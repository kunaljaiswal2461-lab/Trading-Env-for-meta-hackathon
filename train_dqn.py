import os
import sys
import numpy as np
import torch
import argparse
from env.server.trading_environment import TradingEnvironment
from env.models import TradingAction

# Ensure we use the professional agent
try:
    from agent.dqn_agent import DQNAgent
except ImportError:
    from env.agent.dqn_agent import DQNAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=100)
    args = parser.parse_args()

    # Parameters
    state_size = 123
    action_size = 3
    total_episodes = args.episodes
    
    # Init Env & Agent
    env = TradingEnvironment(window=20)
    agent = DQNAgent(state_size=state_size, action_size=action_size)
    
    # Ensure checkpoint dir exists
    os.makedirs("env/checkpoints", exist_ok=True)
    best_score = -float('inf')

    print(f"Starting FIXED UNIFIED training for {total_episodes} episodes...")
    
    for e in range(total_episodes):
        obs = env.reset()
        state = np.array(obs.market_features + [obs.port_cash, obs.holdings, obs.port_val], dtype=np.float32)
        total_reward = 0
        done = False
        
        while not done:
            action = agent.select_action(state)
            
            # Step in environment
            res = env.step(TradingAction(action=action))
            next_state = np.array(res.market_features + [res.port_cash, res.holdings, res.port_val], dtype=np.float32)
            
            # Record experience
            agent.remember(state, action, res.reward, next_state, res.done)
            
            state = next_state
            total_reward += res.reward
            done = res.done
            
            # Train the brain (learn handles target updates internally)
            agent.learn()
            
        # Decay exploration rate
        agent.decay_epsilon()
        
        # Periodic evaluation & Saving
        if (e + 1) % 5 == 0:
            score = total_reward 
            print(f"Episode: {e+1}/{total_episodes}, Reward: {score:.4f}, Epsilon: {agent.epsilon:.2f}")
            
            if score > best_score:
                best_score = score
                agent.save("env/checkpoints/best_model.pt")
                print(f"--> Saved NEW BEST model with reward: {best_score:.4f}")

    print(f"Training Complete. Best Reward: {best_score:.4f}")

if __name__ == "__main__":
    main()
