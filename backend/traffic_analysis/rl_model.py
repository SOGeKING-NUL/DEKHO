import numpy as np
import json
from collections import deque

class TrafficRLAgent:
    def __init__(self, state_size=5, action_size=2):
        self.q_table = np.random.uniform(low=-1, high=1, 
                                       size=(20, 20, 20, 20, 2, action_size))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1
        self.memory = deque(maxlen=2000)
        
    def get_state(self, counts):
        """Normalize counts to discrete bins"""
        return (
            min(counts.get('north', 0)//2, 
            min(counts.get('south', 0)//2,
            min(counts.get('east', 0)//2,
            min(counts.get('west', 0)//2,
            1 if counts.get('emergency', 0) > 0 else 0
        )))))
    
    def choose_action(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(2)
        return np.argmax(self.q_table[state])
    
    def update_model(self, state, action, reward, next_state):
        state = (state,) if isinstance(state, int) else state  # ✅ Ensure state is a tuple
        next_state = (next_state,) if isinstance(next_state, int) else next_state  # ✅ Same for next_state
    
        current_q = self.q_table[state + (action,)]
        max_future_q = np.max(self.q_table[next_state])  # Ensure next_state is tuple

        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)
        self.q_table[state + (action,)] = new_q
        
    def save_model(self, path):
        np.save(path, self.q_table)
        
    def load_model(self, path):
        self.q_table = np.load(path)