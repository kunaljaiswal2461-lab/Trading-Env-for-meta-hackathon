import numpy as np
import pandas as pd
import sys
import os

try:
    from openenv import Environment
except ImportError:
    from openenv_core import Environment

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from env.models import TradingAction, TradingObservation, TradingState
except ModuleNotFoundError:
    from models import TradingAction, TradingObservation, TradingState

class TradingEnvironment(Environment):
    def __init__(self, window=20, initial_capital=10000.0, cost=0.001):
        import os
        # Works both locally (project root/data/) and in Docker (/app/data/)
        THIS_FILE = os.path.abspath(__file__)
        # Try: project_root/data, then /app/data, then relative data/
        for candidate in [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(THIS_FILE))), 'data', 'spy_prices.csv'),
            '/app/data/spy_prices.csv',
            os.path.join(os.path.dirname(THIS_FILE), '..', '..', 'data', 'spy_prices.csv'),
        ]:
            if os.path.exists(candidate):
                csv_path = candidate
                break
        else:
            raise FileNotFoundError('spy_prices.csv not found')
        try:
            from data.preprocess import load_and_preprocess
        except ModuleNotFoundError:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(THIS_FILE)))
            from data.preprocess import load_and_preprocess
        train_df, _ = load_and_preprocess(csv_path)
        self.df = train_df.reset_index(drop=True)
        self.window = window
        self.initial_cash = initial_capital
        self.cost = cost
        self.feat = ['log_return', 'sma5_dist', 'sma20_dist',
                     'rsi', 'norm_volume', 'volatility']
        try:
            from env.reward import RewardCalculator
        except ModuleNotFoundError:
            from reward import RewardCalculator
        self.reward_calc = RewardCalculator(tc_rate=self.cost)
        self._reset_state()

    def _reset_state(self):
        self.cash = self.initial_cash
        self.hold = 0.0
        self.pv = self.initial_cash
        self.peak = self.initial_cash
        self.current_step = self.window
        self.hist = []
        self.trades = 0
        self.done = False
        self.reward_calc.reset()

    def reset(self) -> TradingObservation:
        self._reset_state()
        return self._get_obs(reward=0.0, done=False)

    def step(self, action: TradingAction) -> TradingObservation:
        price = self.df.loc[self.current_step, 'close']
        prev_pv = self.pv
        
        act = action.action  # 0=HOLD, 1=BUY, 2=SELL
        val = (self.hold * price) + self.cash
        rew = 0.0
        done = False
        trade_executed = False
        
        if act == 1 and self.cash > 0:
            self.hold += self.cash / price * (1 - self.cost)
            self.cash = 0
            self.trades += 1
            trade_executed = True
        elif act == 2 and self.hold > 0:
            self.cash += self.hold * price * (1 - self.cost)
            self.hold = 0
            self.trades += 1
            trade_executed = True
            
        self.pv = self.cash + (self.hold * price)
        self.peak = max(self.peak, self.pv)
        
        market_return = float(self.df.iloc[self.current_step]['log_return'])
        rew = self.reward_calc.compute(
            pv=self.pv,
            prev_pv=prev_pv,
            peak=self.peak,
            trade_executed=trade_executed,
            market_return=market_return
        )
        
        self.current_step += 1
        if self.pv < self.initial_cash * 0.5 or self.current_step >= len(self.df) - 1:
            done = True
            
        return self._get_obs(reward=rew, done=done)

    def _get_obs(self, reward, done) -> TradingObservation:
        s = self.current_step
        w = self.window
        feats = self.df.loc[s-w:s-1, self.feat].values.flatten().tolist()
        return TradingObservation(
            market_features=feats,
            port_cash=self.cash,
            holdings=self.hold,
            port_val=self.pv,
            portfolio_value=self.pv,
            current_step=s,
            reward=float(reward),
            done=done
        )

    def state(self) -> TradingState:
        return TradingState(
            portfolio_value=self.pv,
            cash=self.cash,
            holdings=self.hold,
            current_step=self.current_step,
            history=self.hist,
            INITIAL_CASH=int(self.initial_cash),
            TRANSACTION_COST=self.cost
        )
