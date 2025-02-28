import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from traffic_analysis.rl_model import TrafficRLAgent
from traffic_analysis.intersection_sim import VirtualIntersection
import matplotlib.pyplot as plt

def train_rl():
    env = VirtualIntersection()

    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots(figsize=(8, 8))

    for step in range(500):  # Run simulation for 500 steps
        action = step % 2  # Alternate light states (0: NS Green, 1: EW Green)
        state, reward, _ = env.step(action)

        ax.clear()  # Clear previous frame
        env._draw_intersection()  # Redraw updated scene

        plt.pause(0.1)  # Short delay for animation
        time.sleep(0.05)  # Smoothens animation

    plt.ioff()  # Disable interactive mode after loop
    plt.show()  # Final frame

train_rl()