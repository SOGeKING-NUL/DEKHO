import numpy as np
import cv2

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


class TrafficDensityCounter:
    def __init__(self, roi_points=None):
        """
        Initialize a traffic density counter.
        
        Args:
            roi_points: List of points [(x1,y1), (x2,y2), ...] defining the region of interest.
                        If None, the entire frame will be used.
        """
        self.roi_points = roi_points  # Region of interest for density calculation
        self.current_vehicles = set()  # Set of vehicle IDs currently in the ROI
        self.density_history = []  # History of density measurements
        self.max_history = 100  # Maximum history length
        self.debug = True
        
    def set_roi(self, roi_points):
        """Set the region of interest for density calculation."""
        self.roi_points = roi_points
        
    def point_in_roi(self, point):
        """Check if a point is inside the ROI polygon."""
        if self.roi_points is None:
            return True  # If no ROI defined, consider all points inside
            
        # Convert ROI points to numpy array for cv2.pointPolygonTest
        roi_np = np.array(self.roi_points, dtype=np.int32)
        result = cv2.pointPolygonTest(roi_np, point, False)
        return result >= 0  # Return True if point is inside or on the boundary
        
    def update(self, tracks, frame_shape=None):
        """
        Update density count based on tracked vehicles.
        
        Args:
            tracks: List of detection/tracking results in format [x1, y1, x2, y2, id, ...]
            frame_shape: Tuple (height, width) of the frame, used if no ROI is defined
            
        Returns:
            current_density: Number of vehicles currently in the ROI
            density_percentage: Density as a percentage of the ROI area
        """
        # Reset current vehicles for this frame
        self.current_vehicles.clear()
        
        # If no ROI defined but frame shape provided, use the entire frame
        if self.roi_points is None and frame_shape is not None:
            height, width = frame_shape[0:2]
            self.roi_points = [(0, 0), (width, 0), (width, height), (0, height)]
        
        # Process each track
        for track in tracks:
            if len(track) < 6:
                continue
                
            try:
                # Extract track components
                x1 = float(track[0])
                y1 = float(track[1])
                x2 = float(track[2])
                y2 = float(track[3])
                track_id = int(track[4])
                
                # Convert to integers
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                # Calculate center point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Check if vehicle center is in ROI
                if self.point_in_roi((center_x, center_y)):
                    self.current_vehicles.add(track_id)
                    if self.debug:
                        print(f"Vehicle {track_id} in ROI at ({center_x}, {center_y})")
                        
            except (IndexError, ValueError) as e:
                if self.debug:
                    print(f"Error processing track for density: {e}")
                    
        # Calculate current density
        current_density = len(self.current_vehicles)
        
        # Add to history
        self.density_history.append(current_density)
        
        # Maintain history length
        if len(self.density_history) > self.max_history:
            self.density_history = self.density_history[-self.max_history:]
            
        # Calculate density percentage if ROI is defined
        density_percentage = 0
        if current_density > 0 and self.roi_points is not None:
            # This is a simple metric - we could refine it based on average vehicle size
            # and ROI area for a more accurate representation
            roi_area = cv2.contourArea(np.array(self.roi_points, dtype=np.int32))
            avg_vehicle_area = 5000  # Rough estimate in pixels - adjust based on your scale
            occupied_area = current_density * avg_vehicle_area
            density_percentage = min(100, (occupied_area / roi_area) * 100)
            
        return current_density, density_percentage
        
    def draw_roi(self, frame):
        """Draw the ROI polygon on the frame."""
        if self.roi_points is not None:
            roi_np = np.array(self.roi_points, dtype=np.int32)
            cv2.polylines(frame, [roi_np], True, (0, 255, 255), 2)
            
            # Add density information
            current_density = len(self.current_vehicles)
            cv2.putText(frame, f"Vehicles in area: {current_density}", 
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
        return frame