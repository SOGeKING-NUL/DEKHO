import numpy as np
import random
import matplotlib.pyplot as plt
import time
import os

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.5, 
                 exploration_decay=0.99, min_exploration_rate=0.01):
        """
        Initialize Q-Learning agent with parameters
        
        Parameters:
        - state_size: tuple with dimensions of the state space (each dimension's size)
        - action_size: integer representing number of possible actions
        - learning_rate: alpha value for Q-learning update
        - discount_factor: gamma value for future rewards
        - exploration_rate: initial epsilon value for exploration
        - exploration_decay: decay rate for epsilon
        - min_exploration_rate: minimum epsilon value
        """
        # Example state_size for our traffic problem: (5, 5, 5, 5, 2, 5, 5, 5, 5)
        # Representing (north_vehicles, south_vehicles, east_vehicles, west_vehicles, light_ns, emergency_ns, emergency_ew, north_wait, south_wait, east_wait, west_wait)
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        
        # Initialize or load Q-table
        q_table_path = 'q_table.npy'
        if os.path.exists(q_table_path):
            try:
                self.q_table = np.load(q_table_path)
                print(f"Loaded existing Q-table with shape: {self.q_table.shape}")
                
                # Check if dimensions match the current state_size + action_size
                expected_shape = state_size + (action_size,)
                if self.q_table.shape != expected_shape:
                    print(f"Q-table dimensions mismatch. Expected {expected_shape}, but got {self.q_table.shape}. Creating a new Q-table...")
                    self.q_table = np.zeros(expected_shape)
            except Exception as e:
                print(f"Error loading Q-table: {e}")
                self.q_table = np.zeros(state_size + (action_size,))
        else:
            self.q_table = np.zeros(state_size + (action_size,))
            print("Created new Q-table.")
        
        # For tracking performance
        self.rewards_history = []
        
    def choose_action(self, state):
        """Choose an action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            return random.randint(0, self.action_size - 1)
        else:
            # Ensure state indices are within bounds
            bounded_state = self._bound_state(state)
            try:
                return np.argmax(self.q_table[bounded_state])
            except IndexError as e:
                print(f"Index error with state: {bounded_state}, Q-table shape: {self.q_table.shape}")
                return random.randint(0, self.action_size - 1)  # Fallback to random action
    
    def _bound_state(self, state):
        """Ensure state values are within the bounds of the Q-table dimensions"""
        bounded = []
        for i, (dim_val, dim_size) in enumerate(zip(state, self.state_size)):
            # Clamp the value to be within the valid range for that dimension
            bounded.append(max(0, min(dim_val, dim_size - 1)))
        return tuple(bounded)
    
    def update_q_table(self, state, action, reward, next_state, done):
        """Update Q-table using Q-learning algorithm"""
        try:
            # Ensure states are within bounds
            state = self._bound_state(state)
            next_state = self._bound_state(next_state)
            
            # Calculate the Q-learning update
            next_max = np.max(self.q_table[next_state])
            current_q = self.q_table[state + (action,)]
            
            # Q-learning formula
            if done:
                self.q_table[state + (action,)] = reward
            else:
                self.q_table[state + (action,)] = current_q + self.learning_rate * (
                    reward + self.discount_factor * next_max - current_q)
        except IndexError as e:
            print(f"Error updating Q-table: {e}")
            print(f"Index error with state: {state}")
    
    def decay_exploration(self):
        """Decay the exploration rate"""
        self.exploration_rate = max(self.min_exploration_rate, 
                                   self.exploration_rate * self.exploration_decay)
    
    def save_model(self, file_path='q_table.npy'):
        """Save the Q-table to a file"""
        np.save(file_path, self.q_table)
        print(f"Model saved to {file_path}")
    
    def load_model(self, file_path='q_table.npy'):
        """Load the Q-table from a file"""
        try:
            self.q_table = np.load(file_path)
            print(f"Model loaded from {file_path}")
            # Check if dimensions match the current state_size + action_size
            expected_shape = self.state_size + (self.action_size,)
            if self.q_table.shape != expected_shape:
                print(f"Q-table dimensions mismatch. Expected {expected_shape}, but got {self.q_table.shape}. Creating a new Q-table...")
                self.q_table = np.zeros(expected_shape)
        except Exception as e:
            print(f"Could not load model from {file_path}: {e}")
            self.q_table = np.zeros(self.state_size + (self.action_size,))