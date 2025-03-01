# models/area_counter.py
import numpy as np
import cv2

class AreaVehicleCounter:
    """
    A class to count vehicles in a defined area and calculate traffic density.
    Works with any object detection/tracking model that returns bounding boxes.
    """
    def __init__(self, roi_points=None):
        """
        Initialize the area vehicle counter.
        
        Args:
            roi_points: List of (x,y) points defining the region of interest polygon.
                        If None, the entire frame will be used.
        """
        self.roi_points = roi_points
        self.vehicles_in_roi = set()  # Set of vehicle IDs currently in the ROI
        self.density_history = []     # History of density measurements
        self.max_history = 50
        self.density_percentage = 0
        self.avg_vehicle_area = 5000  # Approximate pixel area of average vehicle
        
    def set_roi(self, roi_points):
        """Set or update the region of interest."""
        self.roi_points = roi_points
        
    def is_in_roi(self, point):
        """Check if a point is inside the ROI polygon."""
        if self.roi_points is None:
            return True  # If no ROI defined, consider all points inside
            
        # Convert ROI points to numpy array for cv2.pointPolygonTest
        roi_np = np.array(self.roi_points, dtype=np.int32)
        result = cv2.pointPolygonTest(roi_np, point, False)
        return result >= 0  # Return True if point is inside or on the boundary
    
    def calculate_roi_area(self):
        """Calculate the area of the ROI in square pixels."""
        if self.roi_points is None:
            return 0
            
        roi_np = np.array(self.roi_points, dtype=np.int32)
        return cv2.contourArea(roi_np)
        
    def update(self, detections, frame_shape=None):
        """
        Update vehicle counts based on detections.
        
        Args:
            detections: List of detections in format [x1, y1, x2, y2, id, ...]
            frame_shape: (height, width) of the frame, used if no ROI is defined
            
        Returns:
            count: Number of vehicles in ROI
            percentage: Density percentage
        """
        # Clear previous frame's vehicles
        self.vehicles_in_roi.clear()
        
        # Create default ROI if none exists and frame_shape is provided
        if self.roi_points is None and frame_shape is not None:
            height, width = frame_shape[0:2]
            self.roi_points = [(0, 0), (width, 0), (width, height), (0, height)]
        
        # Calculate ROI area for density percentage
        roi_area = self.calculate_roi_area()
        
        # Process each detection
        for det in detections:
            try:
                # Skip invalid detections
                if len(det) < 5:
                    continue
                    
                # Extract coordinates and ID
                x1, y1, x2, y2 = int(det[0]), int(det[1]), int(det[2]), int(det[3])
                track_id = int(det[4])
                
                # Calculate center point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Check if center is in ROI
                if self.is_in_roi((center_x, center_y)):
                    self.vehicles_in_roi.add(track_id)
            except (ValueError, IndexError):
                # Skip problematic detections
                continue
        
        # Get current count
        count = len(self.vehicles_in_roi)
        
        # Calculate density percentage
        if count > 0 and roi_area > 0:
            # Estimate area occupied by vehicles
            occupied_area = count * self.avg_vehicle_area
            self.density_percentage = min(100, (occupied_area / roi_area) * 100)
        else:
            self.density_percentage = 0
            
        # Update history
        self.density_history.append(count)
        if len(self.density_history) > self.max_history:
            self.density_history = self.density_history[-self.max_history:]
            
        return count, self.density_percentage
        
    def draw_visualization(self, frame, show_vehicle_count=True):
        """
        Draw ROI and statistics on the frame.
        
        Args:
            frame: The video frame to draw on
            show_vehicle_count: Whether to show the vehicle count text
            
        Returns:
            The frame with visualizations added
        """
        # Draw ROI polygon
        if self.roi_points is not None:
            roi_np = np.array(self.roi_points, dtype=np.int32)
            cv2.polylines(frame, [roi_np], True, (0, 255, 255), 2)
            
            # Add semi-transparent overlay to highlight ROI
            overlay = frame.copy()
            cv2.fillPoly(overlay, [roi_np], (0, 255, 255, 64))
            alpha = 0.3
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Display vehicle count and density percentage
        if show_vehicle_count:
            count = len(self.vehicles_in_roi)
            cv2.putText(frame, f"Vehicles in area: {count}", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f"Density: {self.density_percentage:.1f}%", 
                       (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
        return frame