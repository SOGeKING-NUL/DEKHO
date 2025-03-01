import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation
from IPython.display import HTML, display

class VirtualIntersection:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.vehicles = []
        self.emergency_vehicles = []
        self.spawn_rates = {'north': 0.05, 'south': 0.05, 'east': 0.03, 'west': 0.03}
        self.light_states = {'ns': 'red', 'ew': 'green'}  # Starting state
        self.green_timer = 100
        self.traffic_lights = {
            'north': True if self.light_states['ns'] == 'green' else False,
            'south': True if self.light_states['ns'] == 'green' else False,
            'east': True if self.light_states['ew'] == 'green' else False,
            'west': True if self.light_states['ew'] == 'green' else False
        }
        self.wait_times = {'north': 0, 'south': 0, 'east': 0, 'west': 0}
        
        # Initialize visualization
        plt.ion()  # Turn on interactive mode
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Live Traffic Simulation")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.plot_objects = []
        self.current_step = 0  # Track steps manually
        
        # Draw static elements once
        self._draw_roads()

    def _draw_roads(self):
        """Draw static road elements"""
        # Vertical road
        self.ax.add_patch(
            patches.Rectangle((350, 0), 100, 600, facecolor='#333333', zorder=1)
        )
        # Horizontal road
        self.ax.add_patch(
            patches.Rectangle((0, 250), 800, 100, facecolor='#333333', zorder=1)
        )
        # Intersection
        self.ax.add_patch(
            patches.Rectangle((350, 250), 100, 100, facecolor='#555555', zorder=1)
        )
        
        # Road markings
        for i in range(0, 800, 40):
            if i < 350 or i > 450:
                self.ax.add_patch(
                    patches.Rectangle((i, 295), 20, 10, facecolor='white', zorder=2)
                )
        
        for i in range(0, 600, 40):
            if i < 250 or i > 350:
                self.ax.add_patch(
                    patches.Rectangle((395, i), 10, 20, facecolor='white', zorder=2)
                )

    def _draw_vehicles(self):
        """Draw all vehicles"""
        for vehicle in self.vehicles:
            if isinstance(vehicle, dict):
                x, y = vehicle['pos']
                
                # Create vehicle shape based on direction
                direction = vehicle['dir']
                size = vehicle.get('size', 8)
                color = vehicle['color']
                is_emergency = vehicle.get('emergency', False)
                
                if direction in ['north', 'south']:
                    # Create rectangle for vertical moving vehicles
                    width, height = size*1.2, size*2
                    rect = patches.Rectangle(
                        (x-width/2, y-height/2), 
                        width, height, 
                        facecolor=color,
                        edgecolor='white' if is_emergency else 'none',
                        linewidth=2 if is_emergency else 0,
                        zorder=3
                    )
                    self.plot_objects.append(self.ax.add_patch(rect))
                    
                    # Add emergency vehicle lights if needed
                    if is_emergency:
                        light1 = patches.Circle((x-width/4, y-height/4), size/4, facecolor='blue', zorder=4)
                        light2 = patches.Circle((x+width/4, y-height/4), size/4, facecolor='red', zorder=4)
                        self.plot_objects.append(self.ax.add_patch(light1))
                        self.plot_objects.append(self.ax.add_patch(light2))
                        
                else:  # east or west
                    # Create rectangle for horizontal moving vehicles
                    width, height = size*2, size*1.2
                    rect = patches.Rectangle(
                        (x-width/2, y-height/2), 
                        width, height, 
                        facecolor=color,
                        edgecolor='white' if is_emergency else 'none',
                        linewidth=2 if is_emergency else 0,
                        zorder=3
                    )
                    self.plot_objects.append(self.ax.add_patch(rect))
                    
                    # Add emergency vehicle lights if needed
                    if is_emergency:
                        light1 = patches.Circle((x-width/4, y-height/4), size/4, facecolor='blue', zorder=4)
                        light2 = patches.Circle((x+width/4, y-height/4), size/4, facecolor='red', zorder=4)
                        self.plot_objects.append(self.ax.add_patch(light1))
                        self.plot_objects.append(self.ax.add_patch(light2))

    def _draw_lights(self):
        """Draw traffic lights"""
        light_size = 12
        # Traffic light poles
        self.plot_objects.append(self.ax.add_patch(
            patches.Rectangle((400, 350), 5, 150, facecolor='#888888', zorder=2)
        ))
        self.plot_objects.append(self.ax.add_patch(
            patches.Rectangle((400, 100), 5, 150, facecolor='#888888', zorder=2)
        ))
        self.plot_objects.append(self.ax.add_patch(
            patches.Rectangle((250, 300), 100, 5, facecolor='#888888', zorder=2)
        ))
        self.plot_objects.append(self.ax.add_patch(
            patches.Rectangle((450, 300), 100, 5, facecolor='#888888', zorder=2)
        ))
        
        # Traffic light heads
        north_color = 'green' if self.traffic_lights['north'] else 'red'
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((402.5, 500), light_size, facecolor=north_color, zorder=5)
        ))
        south_color = 'green' if self.traffic_lights['south'] else 'red'
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((402.5, 100), light_size, facecolor=south_color, zorder=5)
        ))
        east_color = 'green' if self.traffic_lights['east'] else 'red'
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((550, 302.5), light_size, facecolor=east_color, zorder=5)
        ))
        west_color = 'green' if self.traffic_lights['west'] else 'red'
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((250, 302.5), light_size, facecolor=west_color, zorder=5)
        ))

    def _draw_stats(self):
        """Display statistics"""
        stats_text = (
            f"NS: {'GREEN' if self.light_states['ns'] == 'green' else 'RED'}\n"
            f"EW: {'GREEN' if self.light_states['ew'] == 'green' else 'RED'}\n"
            f"Vehicles: {len(self.vehicles)}\n"
            f"North wait: {self.wait_times['north']}s\n"
            f"South wait: {self.wait_times['south']}s\n"
            f"East wait: {self.wait_times['east']}s\n"
            f"West wait: {self.wait_times['west']}s"
        )
        self.plot_objects.append(self.ax.text(
            20, 550, stats_text, fontsize=12, color='white', 
            verticalalignment='top', zorder=10
        ))

    def update_plot(self):
        """Update visualization for live display"""
        # Clear previous dynamic elements
        while self.plot_objects:
            self.plot_objects.pop().remove()
        
        # Draw dynamic elements
        self._draw_vehicles()
        self._draw_lights()
        self._draw_stats()
        
        # Refresh the figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        # Return the redrawn figure for animation
        return self.fig

    def _change_lights(self, action):
        """Switch the traffic lights based on the action"""
        if action == 0:
            self.light_states = {'ns': 'green', 'ew': 'red'}
        elif action == 1:
            self.light_states = {'ns': 'red', 'ew': 'green'}
        self.green_timer = 100
        self.traffic_lights.update({
            'north': self.light_states['ns'] == 'green',
            'south': self.light_states['ns'] == 'green',
            'east': self.light_states['ew'] == 'green',
            'west': self.light_states['ew'] == 'green'
        })

    def _spawn_vehicles(self):
        for direction in ['north', 'south', 'east', 'west']:
            if random.random() < self.spawn_rates[direction]:
                is_emergency = random.random() < 0.05
                color = 'red' if is_emergency else random.choice([
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', 
                    '#bcbd22', '#17becf'
                ])
                vehicle = {
                    'pos': self._get_spawn_position(direction),
                    'dir': direction,
                    'color': color,
                    'waiting': 0,
                    'emergency': is_emergency,
                    'speed': 3 if is_emergency else 2,
                    'size': 12 if is_emergency else 8
                }
                self.vehicles.append(vehicle)

    def _move_vehicles(self):
        """Move vehicles based on traffic light states and update waiting times."""
        self.wait_times = {'north': 0, 'south': 0, 'east': 0, 'west': 0}
        to_remove = []

        for i, vehicle in enumerate(self.vehicles):
            if not isinstance(vehicle, dict):
                to_remove.append(i)
                continue

            x, y = vehicle['pos']
            direction = vehicle['dir']
            is_emergency = vehicle.get('emergency', False)

            # Check if vehicle is at intersection and should stop
            if is_emergency or self._can_move(direction) or not self._is_at_intersection((x, y)):
                speed = vehicle.get('speed', 2)
                if direction == 'north':
                    vehicle['pos'] = (x, y - speed)
                elif direction == 'south':
                    vehicle['pos'] = (x, y + speed)
                elif direction == 'east':
                    vehicle['pos'] = (x + speed, y)
                elif direction == 'west':
                    vehicle['pos'] = (x - speed, y)
                vehicle['waiting'] = 0
            else:
                vehicle['waiting'] += 1
                self.wait_times[direction] += 1

            # Remove vehicles that have left the screen
            if not self._in_bounds(vehicle['pos']):
                to_remove.append(i)

        # Remove vehicles in reverse order to avoid index issues
        for i in reversed(to_remove):
            self.vehicles.pop(i)

    def _is_at_intersection(self, pos):
        """Check if a position is at the intersection waiting area"""
        x, y = pos
        # Check if position is in the approach to the intersection
        if 350 <= x <= 450 and 250 <= y <= 350:
            return False  # Inside intersection, can continue
            
        # North approach
        if 350 <= x <= 450 and 150 < y < 250:
            return True
            
        # South approach
        if 350 <= x <= 450 and 350 < y < 450:
            return True
            
        # East approach
        if 250 < x < 350 and 250 <= y <= 350:
            return True
            
        # West approach
        if 450 < x < 550 and 250 <= y <= 350:
            return True
            
        return False

    def _can_move(self, direction):
        """Check if a direction can move based on traffic lights"""
        if direction in ['north', 'south']:
            return self.light_states['ns'] == 'green'
        return self.light_states['ew'] == 'green'

    def _calculate_reward(self):
        """Calculate reward based on vehicle flow and waiting times"""
        reward = 0
        # Reward for each vehicle moving
        reward += sum(1 for v in self.vehicles if isinstance(v, dict) and v['waiting'] == 0) * 2
        # Penalty for waiting vehicles
        reward -= sum(v['waiting'] for v in self.vehicles if isinstance(v, dict)) * 0.1
        # Extra penalty for emergency vehicles waiting
        reward -= sum(v['waiting'] * 2 for v in self.vehicles if isinstance(v, dict) and v.get('emergency', False))
        return reward

    def _get_spawn_position(self, direction):
        """Get spawn position for a vehicle based on direction"""
        offset = random.randint(-30, 30)
        if direction == 'north':
            return (400 + offset, self.height - 20)
        elif direction == 'south':
            return (400 + offset, 20)
        elif direction == 'east':
            return (20, 300 + offset)
        elif direction == 'west':
            return (self.width - 20, 300 + offset)

    def _in_bounds(self, pos):
        """Check if a position is within the simulation bounds"""
        x, y = pos
        margin = 30
        return -margin <= x <= self.width + margin and -margin <= y <= self.height + margin

    def reset(self):
        """Reset the simulation"""
        self.vehicles = []
        self.green_timer = 100
        self.light_states = {'ns': 'red', 'ew': 'green'}
        self.traffic_lights.update({
            'north': False,
            'south': False,
            'east': True,
            'west': True
        })
        self.current_step = 0
        return self._get_state()

    def step(self, action):
        """Take a step in the simulation"""
        if action not in [0, 1]:
            raise ValueError("Invalid action. Must be 0 (NS Green) or 1 (EW Green)")
        
        self._change_lights(action)
        self._spawn_vehicles()
        self._move_vehicles()
        self.current_step += 1
        reward = self._calculate_reward()
        done = self.current_step >= 1000
        
        return self._get_state(), reward, done

    def _get_state(self):
        """Get the current state of the simulation"""
        # Count vehicles in each direction, capped at 4 to match Q-table
        counts = {
            'north': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'north')),
            'south': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'south')),
            'east': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'east')),
            'west': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'west'))
        }
        
        # Also count emergency vehicles (capped at 4 for consistency, though not used in Q-table)
        emergency_counts = {
            'north': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'north' and v.get('emergency', False))),
            'south': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'south' and v.get('emergency', False))),
            'east': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'east' and v.get('emergency', False))),
            'west': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'west' and v.get('emergency', False)))
        }
        
        counts.update({'emergency_' + k: v for k, v in emergency_counts.items()})
        counts.update(self.wait_times)
        counts.update({'light_ns': 1 if self.light_states['ns'] == 'green' else 0})
        
        return counts