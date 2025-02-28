import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traffic_analysis.rl_model import TrafficRLAgent
from traffic_analysis.intersection_sim import VirtualIntersection
import matplotlib.pyplot as plt

def train_rl():
    env = VirtualIntersection()
    agent = TrafficRLAgent()
    
    episodes = 1000
    rewards = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = agent.choose_action(agent.get_state(state))
            next_state, reward, done = env.step(action)
            agent.update_model(agent.get_state(state), action, reward, 
                             agent.get_state(next_state))
            
            total_reward += reward
            state = next_state
            env.render()
            
        rewards.append(total_reward)
        print(f"Episode {episode+1}/{episodes} | Reward: {total_reward:.2f}")
        
        # Decay exploration rate
        if episode % 100 == 0:
            agent.epsilon = max(0.01, agent.epsilon * 0.9)
    
    # Save trained model
    agent.save_model('data/simulations/rl_model.npy')
    
    # Plot training progress
    plt.plot(rewards)
    plt.title("Training Progress")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.savefig('data/simulations/training_plot.png')

if __name__ == "__main__":
    train_rl()