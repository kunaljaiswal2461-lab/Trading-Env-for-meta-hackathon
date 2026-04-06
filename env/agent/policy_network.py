"""
PolicyNetwork — 3-layer neural network Q-function approximator.

Input:  state vector of shape (state_size,)  — 120 market features + 3 portfolio = 123
Output: Q-values for each of the 3 discrete actions (HOLD=0, BUY=1, SELL=2)
"""

import torch
import torch.nn as nn


class PolicyNetwork(nn.Module):
    """
    3-layer fully-connected DQN policy network.

    Architecture:
        Linear(state_size → 256) → LayerNorm → LeakyReLU
        Linear(256 → 128)        → LayerNorm → LeakyReLU
        Linear(128 → action_size)               (raw Q-values, no activation)
    """

    def __init__(self, state_size: int = 123, action_size: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.01),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.01),
            nn.Linear(128, action_size),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity='leaky_relu')
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
