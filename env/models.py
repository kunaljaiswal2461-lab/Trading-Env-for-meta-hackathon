from pydantic import BaseModel
from typing import List, Optional

class TradingAction(BaseModel):
    action: int          # 0=HOLD, 1=BUY, 2=SELL

class TradingObservation(BaseModel):
    market_features: List[float]  # window(20) * features(6) = 120 values
    port_cash: float              # cash in bank in USD
    holdings: float               # stocks held
    port_val: float               # (portfolio + holdings) in USD
    portfolio_value: float
    current_step: int
    reward: float = 0.0
    done: bool = False

class TradingState(BaseModel):
    portfolio_value: float
    cash: float
    holdings: float
    current_step: int
    history: list
    INITIAL_CASH: int
    TRANSACTION_COST: float = 0.001
