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
        self.light_states = {'ns': 'red', 'ew': 'green'}  # Starting state: one green, one red
        self.green_timer = 300  # Increased to 300 steps for stability, but adjustable
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
        self.ax.set_title("Live Traffic Simulation (Straight Movement)")
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
        """Draw vehicles as dots (straight movement only)"""
        for vehicle in self.vehicles:
            if isinstance(vehicle, dict):
                x, y = vehicle['pos']
                
                # Create dot for vehicle based on direction
                direction = vehicle['dir']
                size = vehicle.get('size', 5)  # Smaller size for dots
                color = vehicle['color']
                is_emergency = vehicle.get('emergency', False)
                
                # Use dots instead of rectangles or turns
                dot = patches.Circle(
                    (x, y),
                    radius=size,
                    facecolor=color,
                    edgecolor='white' if is_emergency else 'none',
                    linewidth=1 if is_emergency else 0,
                    zorder=3
                )
                self.plot_objects.append(self.ax.add_patch(dot))
                
                # Add emergency vehicle lights as smaller dots if needed
                if is_emergency:
                    light1 = patches.Circle((x - size, y - size), size/2, facecolor='blue', zorder=4)
                    light2 = patches.Circle((x + size, y - size), size/2, facecolor='red', zorder=4)
                    self.plot_objects.append(self.ax.add_patch(light1))
                    self.plot_objects.append(self.ax.add_patch(light2))

    def _draw_lights(self):
        """Draw traffic lights using ns and ew states"""
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
        
        # Traffic light heads (using ns and ew from light_states)
        north_color = 'green' if self.light_states['ns'] == 'green' else 'red'
        south_color = 'green' if self.light_states['ns'] == 'green' else 'red'
        east_color = 'green' if self.light_states['ew'] == 'green' else 'red'
        west_color = 'green' if self.light_states['ew'] == 'green' else 'red'
        
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((402.5, 500), light_size, facecolor=north_color, zorder=5)
        ))
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((402.5, 100), light_size, facecolor=south_color, zorder=5)
        ))
        self.plot_objects.append(self.ax.add_patch(
            patches.Circle((550, 302.5), light_size, facecolor=east_color, zorder=5)
        ))
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

    def update_visuals(self):
        """Update visualization for live display with debugging"""
        try:
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
            print(f"Visualization updated successfully at step {self.current_step}")
            
            # Return the redrawn figure for animation
            return self.fig
        except Exception as e:
            print(f"Error in update_visuals: {e}")
            return None

    def _change_lights(self, action):
        """
        Enhanced traffic light control system with emergency vehicle prioritization
        
        Key features:
        1. Emergency vehicles get absolute priority
        2. Uses a responsive timing mechanism based on traffic conditions
        3. Prevents excessive wait times in any direction
        4. Manages transition states properly for safety
        5. Dynamically adjusts green duration based on current traffic volume
        """
        # Count vehicles and emergencies in each direction
        north_vehicles = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'north')
        south_vehicles = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'south')
        east_vehicles = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'east')
        west_vehicles = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'west')
        
        # Count emergency vehicles in each direction
        north_emergency = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'north' and v.get('emergency', False))
        south_emergency = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'south' and v.get('emergency', False))
        east_emergency = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'east' and v.get('emergency', False))
        west_emergency = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'west' and v.get('emergency', False))
        
        # Get total emergency vehicles per axis
        ns_emergency = north_emergency + south_emergency
        ew_emergency = east_emergency + west_emergency
        
        # Get total regular vehicles per axis
        ns_traffic = north_vehicles + south_vehicles
        ew_traffic = east_vehicles + west_vehicles
        
        # Calculate average waiting times for each direction
        ns_wait = (self.wait_times['north'] + self.wait_times['south']) / 2 if (north_vehicles + south_vehicles) > 0 else 0
        ew_wait = (self.wait_times['east'] + self.wait_times['west']) / 2 if (east_vehicles + west_vehicles) > 0 else 0
        
        # Track if we're about to switch lights (for transition state)
        switch_needed = False
        current_ns_green = self.light_states['ns'] == 'green'
        
        # EMERGENCY VEHICLE PRIORITY LOGIC
        if ns_emergency > 0 and not current_ns_green:
            # Emergency vehicle in NS axis while NS is red - switch immediately
            switch_needed = True
            print("Priority: NS emergency vehicle detected - switching lights")
        elif ew_emergency > 0 and current_ns_green:
            # Emergency vehicle in EW axis while EW is red - switch immediately
            switch_needed = True
            print("Priority: EW emergency vehicle detected - switching lights")
        
        # EXCESSIVE WAIT TIME PREVENTION
        # If any direction has been waiting too long (20+ seconds), prioritize it
        elif ns_wait >= 20 and not current_ns_green:
            switch_needed = True
            print(f"NS excessive wait time ({ns_wait}s) - switching lights")
        elif ew_wait >= 20 and current_ns_green:
            switch_needed = True
            print(f"EW excessive wait time ({ew_wait}s) - switching lights")
        
        # TRAFFIC VOLUME LOGIC
        # If green timer expired, evaluate based on traffic volume
        elif self.green_timer <= 0:
            # Balanced approach based on vehicle counts
            if current_ns_green and ns_traffic < 3 and ew_traffic > 5:
                # Switch from NS to EW if NS traffic is light and EW has queued vehicles
                switch_needed = True
                print(f"Traffic imbalance (NS:{ns_traffic} < EW:{ew_traffic}) - switching lights")
            elif not current_ns_green and ew_traffic < 3 and ns_traffic > 5:
                # Switch from EW to NS if EW traffic is light and NS has queued vehicles
                switch_needed = True
                print(f"Traffic imbalance (EW:{ew_traffic} < NS:{ns_traffic}) - switching lights")
            elif current_ns_green and ns_traffic == 0 and ew_traffic > 0:
                # No vehicles in green direction but vehicles waiting in red direction
                switch_needed = True
                print("No NS traffic but EW vehicles waiting - switching lights")
            elif not current_ns_green and ew_traffic == 0 and ns_traffic > 0:
                # No vehicles in green direction but vehicles waiting in red direction
                switch_needed = True
                print("No EW traffic but NS vehicles waiting - switching lights")
        
        # PERFORM LIGHT SWITCH IF NEEDED
        if switch_needed:
            # Toggle the lights
            new_ns_state = 'red' if current_ns_green else 'green'
            new_ew_state = 'green' if current_ns_green else 'red'
            self.light_states = {'ns': new_ns_state, 'ew': new_ew_state}
            
            # Calculate dynamic green time based on waiting vehicles and emergency status
            if new_ns_state == 'green':
                # NS direction just turned green
                # Base time + adjustment for traffic volume + emergency priority
                base_time = 180  # Minimum green time
                traffic_adjustment = min(ns_traffic * 20, 200)  # More traffic = more time, max 200
                emergency_bonus = ns_emergency * 100  # Emergency vehicles get extra time
                wait_factor = min(ns_wait * 5, 100)  # More wait time = more green time, max 100
                
                self.green_timer = base_time + traffic_adjustment + emergency_bonus + wait_factor
                print(f"NS green time set to {self.green_timer} (traffic:{ns_traffic}, emergency:{ns_emergency}, wait:{ns_wait})")
            else:
                # EW direction just turned green
                base_time = 180
                traffic_adjustment = min(ew_traffic * 20, 200)
                emergency_bonus = ew_emergency * 100
                wait_factor = min(ew_wait * 5, 100)
                
                self.green_timer = base_time + traffic_adjustment + emergency_bonus + wait_factor
                print(f"EW green time set to {self.green_timer} (traffic:{ew_traffic}, emergency:{ew_emergency}, wait:{ew_wait})")
            
            # Cap maximum green time at 500 steps for stability
            self.green_timer = min(self.green_timer, 500)
        
        # Update traffic light states for display
        self.traffic_lights.update({
            'north': self.light_states['ns'] == 'green',
            'south': self.light_states['ns'] == 'green',
            'east': self.light_states['ew'] == 'green',
            'west': self.light_states['ew'] == 'green'
        })
        
        # Decrement green timer
        if self.green_timer > 0:
            self.green_timer -= 1

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
                    'size': 5  # Smaller size for dots
                }
                self.vehicles.append(vehicle)

    def _move_vehicles(self):
        """Move vehicles straight and ensure they cross the junction when lights allow"""
        self.wait_times = {'north': 0, 'south': 0, 'east': 0, 'west': 0}
        to_remove = []

        for i, vehicle in enumerate(self.vehicles):
            if not isinstance(vehicle, dict):
                to_remove.append(i)
                continue

            x, y = vehicle['pos']
            direction = vehicle['dir']
            is_emergency = vehicle.get('emergency', False)

            # Vehicles can move if:
            # 1. They are emergency vehicles (always can move), OR
            # 2. The traffic light for their direction is green
            can_move = is_emergency or self._can_move(direction)
            if can_move:
                speed = vehicle.get('speed', 2)
                new_pos = self._move_straight((x, y), direction, speed)
                vehicle['pos'] = new_pos
                vehicle['waiting'] = 0
                # Ensure vehicles cross the intersection if they enter it
                if self._is_at_intersection((x, y)) and not self._is_at_intersection(new_pos):
                    vehicle['waiting'] = 0  # Reset waiting if crossing
            else:
                vehicle['waiting'] += 1
                self.wait_times[direction] += 1

            # Remove vehicles that have left the screen or reached their destination
            if not self._in_bounds(vehicle['pos']):
                to_remove.append(i)

        # Remove vehicles in reverse order to avoid index issues
        for i in reversed(to_remove):
            self.vehicles.pop(i)

        # Decrement green timer if active
        if self.green_timer > 0:
            self.green_timer -= 1

    def _move_straight(self, pos, direction, speed):
        """Move vehicle straight along its direction, ensuring smooth crossing through the junction"""
        x, y = pos
        if direction == 'north':
            y = max(0, y - speed)
            x = max(350, min(450, x))  # Stay in NS lane
            # If approaching or in intersection, ensure crossing
            if y <= 350 and y > 250:  # In or near intersection
                y = max(0, y - speed)  # Continue moving north
        elif direction == 'south':
            y = min(self.height, y + speed)
            x = max(350, min(450, x))  # Stay in NS lane
            # If approaching or in intersection, ensure crossing
            if y >= 250 and y < 350:  # In or near intersection
                y = min(self.height, y + speed)  # Continue moving south
        elif direction == 'east':
            x = min(self.width, x + speed)
            y = max(250, min(350, y))  # Stay in EW lane
            # If approaching or in intersection, ensure crossing
            if x >= 350 and x < 450:  # In or near intersection
                x = min(self.width, x + speed)  # Continue moving east
        elif direction == 'west':
            x = max(0, x - speed)
            y = max(250, min(350, y))  # Stay in EW lane
            # If approaching or in intersection, ensure crossing
            if x <= 450 and x > 350:  # In or near intersection
                x = max(0, x - speed)  # Continue moving west
        return (x, y)

    def _is_at_intersection(self, pos):
        """Check if a position is at or near the intersection area"""
        x, y = pos
        # Expand intersection area slightly to ensure vehicles can cross (350-450, 240-360)
        return 350 <= x <= 450 and 240 <= y <= 360

    def _can_move(self, direction):
        """Check if a direction can move based on traffic lights, allowing crossing if in intersection"""
        if direction in ['north', 'south']:
            return self.light_states['ns'] == 'green'
        return self.light_states['ew'] == 'green'

    def _calculate_reward(self):
        """Calculate reward based on vehicle flow, waiting times, and light changes (straight movement only)"""
        reward = 0
        # Reward for each vehicle moving (higher to prioritize flow)
        reward += sum(1 for v in self.vehicles if isinstance(v, dict) and v['waiting'] == 0) * 20  # Increased reward
        # Penalty for waiting vehicles (higher penalty to minimize congestion)
        reward -= sum(v['waiting'] for v in self.vehicles if isinstance(v, dict)) * 3.0  # Further increased penalty
        # Extra penalty for emergency vehicles waiting (higher priority)
        reward -= sum(v['waiting'] * 30 for v in self.vehicles if isinstance(v, dict) and v.get('emergency', False))  # Further increased penalty
        # Bonus for keeping lights green when vehicles are moving (higher bonus for efficiency)
        if self.light_states['ns'] == 'green':
            ns_moving = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] in ['north', 'south'] and v['waiting'] == 0)
            reward += ns_moving * 20  # Increased bonus
        if self.light_states['ew'] == 'green':
            ew_moving = sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] in ['east', 'west'] and v['waiting'] == 0)
            reward += ew_moving * 20  # Increased bonus
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
        self.green_timer = 300
        self.light_states = {'ns': 'red', 'ew': 'green'}  # Start with EW green, NS red
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
        # Count vehicles in each direction (straight-moving only), capped at 4
        counts = {
            'north': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'north')),
            'south': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'south')),
            'east': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'east')),
            'west': min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] == 'west'))
        }
        
        # Count emergency vehicles (combined for NS and EW, capped at 4)
        emergency_ns = min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] in ['north', 'south'] and v.get('emergency', False)))
        emergency_ew = min(4, sum(1 for v in self.vehicles if isinstance(v, dict) and v['dir'] in ['east', 'west'] and v.get('emergency', False)))
        
        # Current light state and waiting times for better state representation
        counts.update({'light_ns': 1 if self.light_states['ns'] == 'green' else 0})
        counts.update({'emergency_ns': emergency_ns, 'emergency_ew': emergency_ew})
        counts.update({
            'north_wait': min(4, self.wait_times['north'] // 10),  # Binned waiting times (0-4)
            'south_wait': min(4, self.wait_times['south'] // 10),
            'east_wait': min(4, self.wait_times['east'] // 10),
            'west_wait': min(4, self.wait_times['west'] // 10)
        })
        
        return counts