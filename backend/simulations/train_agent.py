import sys
import os
import signal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from traffic_analysis.ql_agent import QLearningAgent  # Updated import
from traffic_analysis.intersection_sim import VirtualIntersection
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg for GUI (must be set before importing plt)
import matplotlib.pyplot as plt

# Global flag to control simulation exit
running = True

def signal_handler(sig, frame):
    global running
    print('\nSimulation interrupted by user. Saving and exiting...')
    running = False

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def train_agent(episodes=10, max_steps=1000, render=True, save_interval=1, load_model=False):
    """Train the Q-learning agent in the virtual intersection environment"""
    # Create environment
    env = VirtualIntersection()
    
    # State size includes: north_vehicles, south_vehicles, east_vehicles, west_vehicles, light_ns, emergency_ns, emergency_ew, north_wait, south_wait, east_wait, west_wait
    # Each value is bound between 0-4 (5 possible values)
    state_size = (5, 5, 5, 5, 2, 5, 5, 5, 5)  # Expanded state
    action_size = 2  # 0: NS Green, 1: EW Green
    
    # Create agent
    agent = QLearningAgent(state_size, action_size, exploration_rate=0.5, exploration_decay=0.99)  # Adjusted for faster convergence
    
    # Load existing model if specified
    if load_model:
        agent.load_model()
    
    # Training loop
    total_rewards = []
    
    try:
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            for step in range(max_steps):
                if not running:
                    break
                    
                # Choose action
                # Convert state dictionary to tuple (straight-moving vehicles only, with waiting times)
                state_tuple = (
                    min(4, state.get('north', 0)),  # North vehicles
                    min(4, state.get('south', 0)),  # South vehicles
                    min(4, state.get('east', 0)),   # East vehicles
                    min(4, state.get('west', 0)),   # West vehicles
                    1 if state.get('light_ns', 0) == 1 else 0,  # Light state (0 or 1)
                    min(4, state.get('emergency_ns', 0)),  # NS emergencies
                    min(4, state.get('emergency_ew', 0)),  # EW emergencies
                    min(4, state.get('north_wait', 0)),  # North waiting time (binned)
                    min(4, state.get('south_wait', 0)),  # South waiting time (binned)
                    min(4, state.get('east_wait', 0)),   # East waiting time (binned)
                    min(4, state.get('west_wait', 0))    # West waiting time (binned)
                )
                
                action = agent.choose_action(state_tuple)
                # Ensure action is valid (0 or 1) to prevent ValueError
                action = max(0, min(1, action))  # Clamp action to 0 or 1
                
                # Take action
                next_state, reward, done = env.step(action)
                
                # Convert next state to tuple
                next_state_tuple = (
                    min(4, next_state.get('north', 0)),
                    min(4, next_state.get('south', 0)),
                    min(4, next_state.get('east', 0)),
                    min(4, next_state.get('west', 0)),
                    1 if next_state.get('light_ns', 0) == 1 else 0,
                    min(4, next_state.get('emergency_ns', 0)),
                    min(4, next_state.get('emergency_ew', 0)),
                    min(4, next_state.get('north_wait', 0)),
                    min(4, next_state.get('south_wait', 0)),
                    min(4, next_state.get('east_wait', 0)),
                    min(4, next_state.get('west_wait', 0))
                )
                
                # Update Q-table
                agent.update_q_table(state_tuple, action, reward, next_state_tuple, done)
                
                # Update state and accumulate reward
                state = next_state
                total_reward += reward
                
                # Display status
                ns_light = "GREEN" if env.light_states['ns'] == 'green' else "RED"
                print(f"Step {step}, Action: {action}, NS Light: {ns_light}, Vehicles: {len(env.vehicles)}, "
                      f"North Wait: {env.wait_times['north']}, East Wait: {env.wait_times['east']}")
                
                # Render if enabled
                if render and step % 5 == 0:  # Render every 5 steps to improve performance
                    try:
                        result = env.update_visuals()
                        if result is None:
                            print(f"Visualization failed at step {step}")
                        else:
                            print(f"Visualization rendered successfully at step {step}")
                        plt.pause(0.1)  # Maintain slow animation (0.1 seconds per frame)
                    except Exception as e:
                        print(f"Rendering error at step {step}: {e}")
                        # Fallback: save frame as image if TkAgg fails
                        plt.savefig(f'frame_step_{step}.png')
                        plt.clf()
                
                if done:
                    break
            
            # End of episode
            agent.decay_exploration()
            total_rewards.append(total_reward)
            print(f"Episode {episode+1} | Reward: {total_reward:.1f}")
            
            # Save the model at intervals
            if (episode + 1) % save_interval == 0:
                agent.save_model()
        
        # Final save
        agent.save_model()
        
        # Plot rewards
        plt.figure(figsize=(10, 5))
        plt.plot(total_rewards)
        plt.title('Rewards per Episode')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.savefig('rewards.png')
        plt.show()
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user. Saving and exiting...")
        agent.save_model()
        print(f"Episode {episode+1} complete | Steps: {step} | Reward: {total_reward}")
    
    return agent, total_rewards

if __name__ == "__main__":
    agent, rewards = train_agent(episodes=10, max_steps=1000, render=True, save_interval=2, load_model=True)
    print("Model saved.")
    print("Simulation complete.")