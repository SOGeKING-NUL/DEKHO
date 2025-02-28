import cv2
import numpy as np
import random

class VirtualIntersection:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.vehicles = []
        self.emergency_vehicles = []  # ✅ Add this line
        self.spawn_rates = {'north': 0.05, 'south': 0.05, 'east': 0.03, 'west': 0.03}
        self.light_states = {'ns': 'green', 'ew': 'red'}
        self.wait_times = {'north': 0, 'south': 0, 'east': 0, 'west': 0}
    
    def _change_lights(self, action):
        """Update traffic lights based on RL action"""
        if action == 0:  # North-South green
            self.light_states = {'ns': 'green', 'ew': 'red'}
        elif action == 1:  # East-West green
            self.light_states = {'ns': 'red', 'ew': 'green'}

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
        to_remove = []
        for i, vehicle in enumerate(self.vehicles):
            x, y = vehicle['pos']
            can_move = self._can_move(vehicle['dir'])

            if can_move:
                if vehicle['dir'] == 'north':
                    vehicle['pos'] = (x, y - 2)
                elif vehicle['dir'] == 'south':
                    vehicle['pos'] = (x, y + 2)
                elif vehicle['dir'] == 'east':
                    vehicle['pos'] = (x + 2, y)
                elif vehicle['dir'] == 'west':
                    vehicle['pos'] = (x - 2, y)
                vehicle['waiting'] = 0
            else:
                vehicle['waiting'] += 1

            if not self._in_bounds(vehicle['pos']):
                to_remove.append(i)
                if vehicle in self.emergency_vehicles:  # ✅ Remove emergency vehicles properly
                    self.emergency_vehicles.remove(vehicle)

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
        # Penalize waiting vehicles
        reward -= sum(v['waiting'] for v in self.vehicles) * 0.1
        # Reward vehicles that exited
        reward += len(self.emergency_vehicles) * 10
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
    
    def render(self):
        # Create blank canvas
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
    
        # Draw roads
        cv2.line(canvas, (self.width//2 - 100, 0), (self.width//2 - 100, self.height), 
                (200, 200, 200), 300)  # Vertical road (NS)
        cv2.line(canvas, (0, self.height//2 - 100), (self.width, self.height//2 - 100), 
                (200, 200, 200), 300)  # Horizontal road (EW)
    
        # Draw intersection area
        cv2.rectangle(canvas, 
                    (self.width//2 - 100, self.height//2 - 100),
                    (self.width//2 + 100, self.height//2 + 100),
                    (100, 100, 100), -1)
    
        # Draw traffic lights
        light_size = 20
        # North-South lights
        ns_color = (0, 255, 0) if self.light_states['ns'] == 'green' else (0, 0, 255)
        cv2.circle(canvas, (self.width//2 - 120, self.height//2), light_size, ns_color, -1)
        cv2.circle(canvas, (self.width//2 + 120, self.height//2), light_size, ns_color, -1)
    
        # East-West lights
        ew_color = (0, 255, 0) if self.light_states['ew'] == 'green' else (0, 0, 255)
        cv2.circle(canvas, (self.width//2, self.height//2 - 120), light_size, ew_color, -1)
        cv2.circle(canvas, (self.width//2, self.height//2 + 120), light_size, ew_color, -1)
    
        # Draw vehicles
        for vehicle in self.vehicles:
            x, y = map(int, vehicle['pos'])
            size = 8
            # Draw different shapes for directions
            if vehicle['dir'] in ['north', 'south']:
                cv2.rectangle(canvas, 
                            (x - size, y - size),
                            (x + size, y + size),
                            vehicle['color'], -1)
            else:
                cv2.circle(canvas, (x, y), size, vehicle['color'], -1)
    
        # Add info overlay
        cv2.putText(canvas, f"NS: {self.light_states['ns'].upper()}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(canvas, f"EW: {self.light_states['ew'].upper()}", (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(canvas, f"Vehicles: {len(self.vehicles)}", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
        # Display waiting times
        y_offset = 120
        for dir, time in self.wait_times.items():
            cv2.putText(canvas, f"{dir.capitalize()} wait: {time}s", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 1)
            y_offset += 30
    
        # Show simulation
        cv2.imshow("Traffic Intersection Simulation", canvas)
        key = cv2.waitKey(30)
    
        # Emergency vehicle spawn on spacebar
        if key == 32:  # Spacebar
            self._spawn_emergency_vehicle()
    
        return key