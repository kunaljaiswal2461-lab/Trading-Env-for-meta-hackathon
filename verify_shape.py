import sys
from server.trading_environment import TradingEnvironment
from client import TradingEnv
from models import TradingObservation

env = TradingEnvironment()
obs = env.reset()

import numpy as np
arr = np.array(obs.market_features + [obs.port_cash, obs.holdings, obs.port_val], dtype=np.float32)
print('Array shape:', arr.shape)
print('Expected:   (123,)')
print('Match:', arr.shape == (123,))
