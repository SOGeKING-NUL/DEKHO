# models/area_counter.py
import numpy as np
import cv2

class AreaVehicleCounter:
    """
    A class to count vehicles in a defined area and calculate traffic density.
    Works with any object detection/tracking model that returns bounding boxes.
    """
    def __init__(self, roi_points=None):
        self.roi_points = roi_points
        self.vehicles_in_roi = set()
        self.density_history = []
        self.max_history = 50
        self.density_percentage = 0
        self.avg_vehicle_area = 5000
    
    def set_roi(self, roi_points):
        self.roi_points = roi_points
        
    def is_in_roi(self, point):
        if self.roi_points is None:
            return True
        roi_np = np.array(self.roi_points, dtype=np.int32)
        return cv2.pointPolygonTest(roi_np, point, False) >= 0
    
    def calculate_roi_area(self):
        if self.roi_points is None:
            return 0
        roi_np = np.array(self.roi_points, dtype=np.int32)
        return cv2.contourArea(roi_np)
        
    def update(self, detections, frame_shape=None):
        self.vehicles_in_roi.clear()

        # **Increase ROI size dynamically**
        if self.roi_points is None and frame_shape is not None:
            height, width = frame_shape[:2]
            roi_x = int(width * 0.05)   # Start at 5% of width
            roi_y = int(height * 0.2)   # Start at 20% of height
            roi_w = int(width * 0.90)   # Width is 90% of frame
            roi_h = int(height * 0.60)  # Height is 60% of frame

            self.roi_points = [(roi_x, roi_y), (roi_x + roi_w, roi_y),
                               (roi_x + roi_w, roi_y + roi_h), (roi_x, roi_y + roi_h)]

        roi_area = self.calculate_roi_area()
        
        for det in detections:
            if len(det) < 5:
                continue
            try:
                x1, y1, x2, y2, track_id = map(int, det[:5])
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                if self.is_in_roi((center_x, center_y)):
                    self.vehicles_in_roi.add(track_id)
            except ValueError:
                continue
        
        count = len(self.vehicles_in_roi)
        if count > 0 and roi_area > 0:
            occupied_area = count * self.avg_vehicle_area
            self.density_percentage = min(100, (occupied_area / roi_area) * 100)
        else:
            self.density_percentage = 0
        
        self.density_history.append(count)
        if len(self.density_history) > self.max_history:
            self.density_history = self.density_history[-self.max_history:]
        
        return count, self.density_percentage
    
    def draw_visualization(self, frame):
        if self.roi_points is not None:
            roi_np = np.array(self.roi_points, dtype=np.int32)
            cv2.polylines(frame, [roi_np], True, (0, 255, 255), 2)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [roi_np], (0, 255, 255, 64))
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        count = len(self.vehicles_in_roi)
        cv2.putText(frame, f"Vehicles in area: {count}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"Density: {self.density_percentage:.1f}%", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return frame
