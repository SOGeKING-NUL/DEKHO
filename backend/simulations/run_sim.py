import sys
import os
import signal
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the simulation and agent
from traffic_analysis.intersection_sim import VirtualIntersection

# Import RL agent with error handling
try:
    from traffic_analysis.rl_model import TrafficRLAgent
    has_rl_agent = True
except ImportError:
    has_rl_agent = False
    print("RL agent not found. Running in manual mode.")

# Global flag to control simulation exit
running = True

def signal_handler(sig, frame):
    global running
    print('\nSimulation interrupted by user. Saving and exiting...')
    running = False

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def run_simulation():
    # Create the simulation environment
    env = VirtualIntersection()
    
    # Create agent if available
    if has_rl_agent:
        agent = TrafficRLAgent()
        mode = "RL Agent"
    else:
        mode = "Random"
    
    print(f"Running simulation in {mode} mode...")
    
    try:
        # Main simulation loop
        for episode in range(5):  # Run for 5 episodes
            if not running:
                break
                
            state = env.reset()
            total_reward = 0
            step_count = 0
            
            print(f"Episode {episode+1} started")
            
            # Episode loop
            while step_count < 200 and running:  # Run each episode for 200 steps
                try:
                    # Choose action based on mode
                    if has_rl_agent:
                        state_tuple = agent.get_state(state)
                        action = agent.choose_action(state_tuple)
                    else:
                        # Simple rule-based logic if no RL agent
                        ns_waiting = state.get('north', 0) + state.get('south', 0)
                        ew_waiting = state.get('east', 0) + state.get('west', 0)
                        light_ns = state.get('light_ns', 0)
                        
                        # Switch lights based on traffic volume
                        if ns_waiting > ew_waiting * 1.5 and light_ns == 0:
                            action = 0  # Set NS to green
                        elif ew_waiting > ns_waiting * 1.5 and light_ns == 1:
                            action = 1  # Set EW to green
                        elif step_count % 50 == 0:  # Switch every 50 steps otherwise
                            action = 1 - light_ns
                        else:
                            action = light_ns  # Keep current state
                    
                    # Take action in environment
                    next_state, reward, done = env.step(action)
                    total_reward += reward
                    
                    # Update the agent if available
                    if has_rl_agent:
                        next_state_tuple = agent.get_state(next_state)
                        agent.update_model(state_tuple, action, reward, next_state_tuple)
                    
                    # Update visualization
                    env.update_plot()
                    
                    # Update for next step
                    state = next_state
                    step_count += 1
                    
                    # Slow down simulation for visibility
                    time.sleep(0.05)
                    
                    if done:
                        break
                
                except Exception as e:
                    print(f"Error during simulation step: {e}")
                    if step_count > 0:
                        step_count += 1
                        continue
                    else:
                        raise e
            
            print(f"Episode {episode+1} complete | Steps: {step_count} | Reward: {total_reward:.1f}")
            
    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if has_rl_agent:
            try:
                agent.save_model('q_table.npy')
                print("Model saved.")
            except Exception as e:
                print(f"Error saving model: {e}")
        
        # Close plot to clean up
        plt.close()
        print("Simulation complete.")

if __name__ == "__main__":
    run_simulation()