"""
ReplayBuffer — circular experience memory for DQN training.

Stores (state, action, reward, next_state, done) tuples.
Supports uniform random sampling to break temporal correlations.
"""

import random
import numpy as np
from collections import deque
from typing import Tuple


class ReplayBuffer:
    """
    Fixed-size circular replay buffer.

    Args:
        capacity: Maximum number of experiences to store. Oldest are evicted when full.
    """

    def __init__(self, capacity: int = 50_000):
        self.buffer: deque = deque(maxlen=capacity)

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Add a single transition to the buffer."""
        self.buffer.append((
            np.array(state, dtype=np.float32),
            int(action),
            float(reward),
            np.array(next_state, dtype=np.float32),
            bool(done),
        ))

    def sample(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample a random minibatch.

        Returns:
            states:      (batch_size, state_size)  float32
            actions:     (batch_size,)             int64
            rewards:     (batch_size,)             float32
            next_states: (batch_size, state_size)  float32
            dones:       (batch_size,)             float32
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states,      dtype=np.float32),
            np.array(actions,     dtype=np.int64),
            np.array(rewards,     dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones,       dtype=np.float32),
        )

    def __len__(self) -> int:
        return len(self.buffer)

    def is_ready(self, batch_size: int) -> bool:
        """Return True when enough experiences are stored to sample."""
        return len(self) >= batch_size
