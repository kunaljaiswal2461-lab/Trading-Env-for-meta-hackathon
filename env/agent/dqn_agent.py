"""
DQNAgent — epsilon-greedy agent with online/target network architecture.

Implements:
  - Epsilon-greedy exploration with linear decay
  - Double-DQN: online network selects action, target network evaluates value
  - Soft target network updates (tau-weighted Polyak averaging)
  - Model save/load for checkpointing
"""

import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .policy_network import PolicyNetwork
from .replay_buffer import ReplayBuffer


class DQNAgent:
    """
    Deep Q-Network agent with Double-DQN and soft target updates.

    Args:
        state_size:     Dimensionality of the observation vector (default 123).
        action_size:    Number of discrete actions (default 3: HOLD/BUY/SELL).
        lr:             Adam learning rate.
        gamma:          Discount factor for future rewards.
        epsilon:        Initial exploration rate.
        epsilon_min:    Minimum exploration rate after decay.
        epsilon_decay:  Multiplicative decay applied each call to decay_epsilon().
        tau:            Soft update rate for target network Polyak averaging.
        batch_size:     Minibatch size drawn from ReplayBuffer.
        buffer_size:    Capacity of the ReplayBuffer.
        device:         Torch device string ('cpu', 'cuda', 'mps').
    """

    def __init__(
        self,
        state_size: int = 123,
        action_size: int = 3,
        lr: float = 3e-4,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        tau: float = 0.005,
        batch_size: int = 64,
        buffer_size: int = 50_000,
        device: str = "cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.tau = tau
        self.batch_size = batch_size
        self.device = torch.device(device)

        # Online network (trained) and frozen target network
        self.online_net = PolicyNetwork(state_size, action_size).to(self.device)
        self.target_net = PolicyNetwork(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.online_net.parameters(), lr=lr)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss — more stable than MSE

        self.memory = ReplayBuffer(buffer_size)

        self._step_count = 0

    # ------------------------------------------------------------------
    # Action selection
    # ------------------------------------------------------------------

    def select_action(self, state: np.ndarray) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        self.online_net.eval()
        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_vals = self.online_net(state_t)
        self.online_net.train()
        return int(q_vals.argmax(dim=1).item())

    def decay_epsilon(self) -> None:
        """Decay epsilon multiplicatively, clamped to epsilon_min."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def remember(self, state, action, reward, next_state, done) -> None:
        """Store a transition in the replay buffer."""
        self.memory.push(state, action, reward, next_state, done)

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    def learn(self) -> float | None:
        """
        Sample a minibatch and perform one gradient update.

        Returns:
            Loss value as a Python float, or None if buffer is not yet ready.
        """
        if not self.memory.is_ready(self.batch_size):
            return None

        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        states_t      = torch.FloatTensor(states).to(self.device)
        actions_t     = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards_t     = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t       = torch.FloatTensor(dones).to(self.device)

        # Current Q(s, a)
        q_values = self.online_net(states_t).gather(1, actions_t).squeeze(1)

        # Double-DQN target: online selects action, target evaluates value
        with torch.no_grad():
            next_actions = self.online_net(next_states_t).argmax(dim=1, keepdim=True)
            next_q       = self.target_net(next_states_t).gather(1, next_actions).squeeze(1)
            targets      = rewards_t + (1.0 - dones_t) * self.gamma * next_q

        loss = self.loss_fn(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=10.0)
        self.optimizer.step()

        # Soft target update
        self._soft_update()
        self._step_count += 1

        return float(loss.item())

    def _soft_update(self) -> None:
        """Polyak-average target ← tau*online + (1-tau)*target."""
        for t_param, o_param in zip(self.target_net.parameters(), self.online_net.parameters()):
            t_param.data.copy_(self.tau * o_param.data + (1.0 - self.tau) * t_param.data)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        torch.save({
            "online_state_dict":  self.online_net.state_dict(),
            "target_state_dict":  self.target_net.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "epsilon":            self.epsilon,
            "step_count":         self._step_count,
        }, path)

    def load(self, path: str) -> None:#this has been made to this more convenient
        ckpt = torch.load(path, map_location=self.device)
        self.online_net.load_state_dict(ckpt["online_state_dict"])
        self.target_net.load_state_dict(ckpt["target_state_dict"])
        self.optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        self.epsilon    = ckpt.get("epsilon", self.epsilon_min)
        self._step_count = ckpt.get("step_count", 0)
        self.online_net.train()
        self.target_net.eval()
