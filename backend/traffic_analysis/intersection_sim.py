import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class VirtualIntersection:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.vehicles = []
        self.emergency_vehicles = []
        self.spawn_rates = {'north': 0.05, 'south': 0.05, 'east': 0.03, 'west': 0.03}
        self.light_states = {'ns': 'green', 'ew': 'red'}
        self.green_timer = 100
        self.traffic_lights = {
            'north': True if self.light_states['ns'] == 'green' else False,
            'south': True if self.light_states['ns'] == 'green' else False,
            'east': True if self.light_states['ew'] == 'green' else False,
            'west': True if self.light_states['ew'] == 'green' else False
        }
    
    def _change_lights(self, action):
        if self.green_timer <= 0:
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
            if random.random() < self.spawn_rates[direction]:  # ✅ Ensure vehicle is assigned
                is_emergency = random.random() < 0.1  # 10% chance of emergency vehicle
                vehicle = {
                'pos': self._get_spawn_position(direction),
                'dir': direction,
                'color': (0, 0, 255) if is_emergency else tuple(np.random.randint(0, 255, 3).tolist()),
                'waiting': 0,
                'emergency': is_emergency
                }
                self.vehicles.append(vehicle)  # ✅ Now `vehicle` is always defined


    def _move_vehicles(self):
        """Move vehicles based on traffic light states and update waiting times."""

        # Reset waiting times before counting
        self.wait_times = {'north': 0, 'south': 0, 'east': 0, 'west': 0}

        to_remove = []

        for i, vehicle in enumerate(self.vehicles):
            x, y = vehicle['pos']
            direction = vehicle['dir']
            is_emergency = vehicle.get('emergency', False)

            # Emergency vehicles always move, regardless of light
            if is_emergency or self._can_move(direction):
                speed = vehicle.get('speed', 2)  # Default speed = 2

                if direction == 'north':
                    vehicle['pos'] = (x, y - speed)
                elif direction == 'south':
                    vehicle['pos'] = (x, y + speed)
                elif direction == 'east':
                    vehicle['pos'] = (x + speed, y)
                elif direction == 'west':
                    vehicle['pos'] = (x - speed, y)

                vehicle['waiting'] = 0  # Reset waiting time on movement
            else:
                vehicle['waiting'] += 1
                self.wait_times[direction] += 1  # Accumulate waiting time per direction

            # Mark vehicle for removal if out of bounds
            if not self._in_bounds(vehicle['pos']):
                to_remove.append(i)

        # Remove vehicles safely in reverse order to avoid index shift
        for i in reversed(to_remove):
            del self.vehicles[i]
        



    def _can_move(self, direction):
        """Check if vehicle can move based on traffic lights"""
        if direction in ['north', 'south']:
            return self.light_states['ns'] == 'green'
        return self.light_states['ew'] == 'green'

    def _calculate_reward(self):
        """Calculate reward for RL agent"""
        reward = 0
        # Reward reducing waiting time
        reward += sum(v['waiting'] for v in self.vehicles if v['waiting'] == 0) * 2
        reward -= sum(v['waiting'] for v in self.vehicles) * 0.1  # Penalize waiting vehicles
        return reward

    def _get_spawn_position(self, direction):
        """Get starting position for new vehicles"""
        if direction == 'north':
            return (self.width//2, self.height - 50)
        elif direction == 'south':
            return (self.width//2, 50)
        elif direction == 'east':
            return (50, self.height//2)
        elif direction == 'west':
            return (self.width - 50, self.height//2)

    def _in_bounds(self, pos):
        """Check if position is within screen bounds"""
        x, y = pos
        return 0 <= x <= self.width and 0 <= y <= self.height

    def reset(self):
        self.vehicles = []
        return self._get_state()
        
    def step(self, action):
        # Change traffic lights based on RL action
        self._change_lights(action)
        
        # Simulate vehicle movement
        self._spawn_vehicles()
        self._move_vehicles()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        return self._get_state(), reward, False
        
    def _get_state(self):
        counts = {
            'north': sum(1 for v in self.vehicles if v['dir'] == 'north'),
            'south': sum(1 for v in self.vehicles if v['dir'] == 'south'),
            'east': sum(1 for v in self.vehicles if v['dir'] == 'east'),
            'west': sum(1 for v in self.vehicles if v['dir'] == 'west')
        }
        return counts
    
    def _draw_intersection(self):
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)
        ax.set_facecolor('black')
        
        ax.add_patch(patches.Rectangle((-50, -10), 100, 20, facecolor='#333333'))
        ax.add_patch(patches.Rectangle((-10, -50), 20, 100, facecolor='#333333'))
        ax.add_patch(patches.Rectangle((-10, -10), 20, 20, facecolor='#444444'))

        light_positions = {'north': (0, 40), 'south': (0, -40), 'east': (40, 0), 'west': (-40, 0)}
        for direction, pos in light_positions.items():
            color = 'green' if self.traffic_lights[direction] else 'red'
            ax.add_patch(patches.Circle(pos, 5, color=color, alpha=0.8, lw=2, ec='yellow'))

        for vehicle in self.vehicles:
            x, y = vehicle['pos']
            direction = vehicle['dir']
            color = '#00FFFF' if vehicle.get('emergency', False) else '#FF5733'
            width, height = (6, 12) if direction in ['north', 'south'] else (12, 6)
            ax.add_patch(patches.FancyBboxPatch(
                (x - width / 2, y - height / 2), width, height,
                facecolor=color, edgecolor='white', boxstyle='round,pad=0.1'
            ))
        
        ax.text(-48, 42, f'Vehicles: {len(self.vehicles)}', fontsize=10, color='white', weight='bold')
        plt.axis("off")
        plt.pause(0.1)  # Allow animation effect
        plt.show(block=False)