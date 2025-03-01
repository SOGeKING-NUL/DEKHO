import numpy as np
import os

class TrafficRLAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.2):
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        
        # State space definition:
        # More simplified state space to match existing Q-table
        # - Number of cars in each direction (0-5, >5)
        # - Current light state (0, 1)
        self.state_space_size = (6, 6, 6, 6, 2)
        self.action_space_size = 2  # 0: NS Green, 1: EW Green
        
        # Initialize or load Q-table
        if os.path.exists('q_table.npy'):
            try:
                self.q_table = np.load('q_table.npy')
                print(f"Loaded existing Q-table with shape: {self.q_table.shape}")
                
                # Check if dimensions match our current definition
                if len(self.q_table.shape) != len(self.state_space_size) + 1:
                    print("Q-table dimensions mismatch. Creating a new Q-table...")
                    self.q_table = np.zeros(self.state_space_size + (self.action_space_size,))
            except Exception as e:
                print(f"Error loading Q-table: {e}")
                self.q_table = np.zeros(self.state_space_size + (self.action_space_size,))
        else:
            self.q_table = np.zeros(self.state_space_size + (self.action_space_size,))
            print("Created new Q-table.")
        
        self.episode_steps = 0
    
    def get_state(self, env_state):
        """Convert environment state dict to a tuple for Q-table lookup"""
        # Convert vehicle counts to discrete bins (0-4)
        north_vehicles = min(4, env_state.get('north', 0))  # Changed from min(5, ...) to min(4, ...)
        south_vehicles = min(4, env_state.get('south', 0))  # Changed from min(5, ...) to min(4, ...)
        east_vehicles = min(4, env_state.get('east', 0))    # Changed from min(5, ...) to min(4, ...)
        west_vehicles = min(4, env_state.get('west', 0))    # Changed from min(5, ...) to min(4, ...)
        
        # Current light state
        light_ns = 1 if env_state.get('light_ns', 0) == 1 else 0
        
        # Return state tuple
        return (north_vehicles, south_vehicles, east_vehicles, west_vehicles, light_ns)
    
    def choose_action(self, state):
        """Select action using epsilon-greedy policy"""
        self.episode_steps += 1
        
        # Decrease exploration rate over time
        if self.episode_steps % 1000 == 0:
            self.epsilon = max(0.05, self.epsilon * 0.95)
        
        try:
            # Explore: choose random action
            if np.random.random() < self.epsilon:
                return np.random.randint(0, self.action_space_size)
            
            # Exploit: choose best action
            return np.argmax(self.q_table[state])
        except IndexError:
            print(f"Index error with state: {state}")
            return np.random.randint(0, self.action_space_size)
    
    def update_model(self, state, action, reward, next_state):
        """Update Q-table using Q-learning algorithm"""
        try:
            # Current Q-value
            current_q = self.q_table[state + (action,)]
            
            # Maximum Q-value for next state
            max_next_q = np.max(self.q_table[next_state])
            
            # Q-learning update formula
            new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
            
            # Update Q-table
            self.q_table[state + (action,)] = new_q
        except IndexError as e:
            print(f"Error updating Q-table: {e}")
    
    def save_model(self, filepath='q_table.npy'):
        """Save Q-table to file"""
        np.save(filepath, self.q_table)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='q_table.npy'):
        """Load Q-table from file"""
        if os.path.exists(filepath):
            self.q_table = np.load(filepath)
            print(f"Model loaded from {filepath}")
            return True
        return False