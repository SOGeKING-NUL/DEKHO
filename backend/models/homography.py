# # models/homography.py
# class VirtualLineCounter:
#     def __init__(self, line_y):
#         self.line_y = line_y  # horizontal line positioning
#         self.counts = {'north': 0, 'south': 0}  # counts of vehicles crossing the line
#         self.track_history = {}  # stores the y-positions of tracks by ID
#         self.debug=True  #debug mode
    
#     def update(self, tracks):
#         for track in tracks:
#             # The track format is [x1, y1, x2, y2, id, confidence, class_id, ...]
#             # Extract just what we need
#             x1, y1, x2, y2, track_id = track[0:5]
            
#             # Convert to integers
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#             track_id = int(track_id)
            
#             # Calculate center position
#             x_center = (x1 + x2) // 2
#             y_center = (y1 + y2) // 2
            
#             # Initialize track history if this is a new track ID
#             if track_id not in self.track_history:
#                 self.track_history[track_id] = []
#                 self.track_history[track_id].append(y_center)
#                 if self.debug:
#                     print(f"New track ID {track_id} added to history")
#                 continue

#             #getting prev position
#             prev_y = self.track_history[track_id][-1]
            
#             # Check if the line is crossed
#             if (prev_y <= self.line_y and y_center > self.line_y):
#                 self.counts['south'] += 1
#                 if self.debug:
#                     print(f"Vehicle {track_id} crossed southbound: {prev_y} -> {y_center}, line at {self.line_y}")
            
#             elif (prev_y >= self.line_y and y_center < self.line_y):
#                 self.counts['north'] += 1
#                 if self.debug:
#                     print(f"Vehicle {track_id} crossed northbound: {prev_y} -> {y_center}, line at {self.line_y}")
            
#             # Add current position to track history
#             self.track_history[track_id].append(y_center)
            
#             # Optional: Limit history length to prevent memory issues
#             if len(self.track_history[track_id]) > 50:
#                 self.track_history[track_id] = self.track_history[track_id][-50:]

# models/homography.py
import numpy as np

class VirtualLineCounter:
    def __init__(self, line_y):
        self.line_y = line_y  # Horizontal line position (y-coordinate)
        self.counts = {'north': 0, 'south': 0}
        self.track_history = {}  # {track_id: [y_centers]}
        self.debug = True
        self.max_history = 20  # Limit track history length

    def update(self, tracks):
        for track in tracks:
            # Validate track format
            if len(track) < 6:
                if self.debug:
                    print(f"Invalid track format: {track}")
                continue

            try:
                # Extract track components with proper typing
                x1 = float(track[0])
                y1 = float(track[1])
                x2 = float(track[2])
                y2 = float(track[3])
                track_id = int(track[4])
            except (IndexError, ValueError) as e:
                if self.debug:
                    print(f"Track parsing error: {e}")
                continue

            # Convert to integers for pixel coordinates
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            y_center = (y1 + y2) // 2

            # Initialize new tracks
            if track_id not in self.track_history:
                self.track_history[track_id] = [y_center]
                if self.debug:
                    print(f"New track {track_id} @ {y_center}")
                continue

            # Get movement direction
            prev_y = self.track_history[track_id][-1]
            self.track_history[track_id].append(y_center)

            # Check line crossing with hysteresis
            if len(self.track_history[track_id]) > 1:
                if prev_y <= self.line_y and y_center > self.line_y:
                    self.counts['south'] += 1
                    if self.debug:
                        print(f"Southbound: {track_id} ({prev_y}→{y_center})")
                        
                elif prev_y >= self.line_y and y_center < self.line_y:
                    self.counts['north'] += 1
                    if self.debug:
                        print(f"Northbound: {track_id} ({prev_y}→{y_center})")

            # Maintain history length
            if len(self.track_history[track_id]) > self.max_history:
                self.track_history[track_id] = self.track_history[track_id][-self.max_history:]