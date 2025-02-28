import numpy as np
import json
from collections import deque

class TrafficRLAgent:
    def __init__(self, state_size=5, action_size=2):

        # State: [north, south, east, west] counts binned (0-4) + emergency flag
        self.state_size = 5
        self.action_size = 2  # 0=NS-green, 1=EW-green
        
        # Q-table dimensions: (north_bins, south_bins, east_bins, west_bins, emergency_flag, actions)
        self.q_table = np.zeros((5, 5, 5, 5, 2, self.action_size))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1
        self.bin_size = 5  #Vehicles per bin
        
    def get_state(self, counts):
        """Convert counts to discrete state bins (0-4)"""
        return (
            min(counts.get('north', 0) // self.bin_size, 4),
            min(counts.get('south', 0) // self.bin_size, 4),
            min(counts.get('east', 0) // self.bin_size, 4),
            min(counts.get('west', 0) // self.bin_size, 4),
            1 if counts.get('emergency', False) else 0
        )
    
    def choose_action(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        return np.argmax(self.q_table[state])
    
    def update_model(self, state, action, reward, next_state):
        current_q = self.q_table[state + (action,)]
        max_future_q = np.max(self.q_table[next_state])
        
        new_q = (1 - self.learning_rate) * current_q + \
                self.learning_rate * (reward + self.discount_factor * max_future_q)
        self.q_table[state + (action,)] = new_q
        
    def save_model(self, path):
        np.save(path, self.q_table)
        
    def load_model(self, path):
        self.q_table = np.load(path)