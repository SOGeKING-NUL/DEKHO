# main.py
import cv2
import numpy as np
import os

# Import only what's needed
try:
    from models.yolo_model import VehicleCounter
    from models.area_counter import AreaVehicleCounter
except ImportError:
    print("Error importing required modules. Make sure all modules are in the correct location.")
    exit(1)

def main():
    print("Initializing Traffic Density Counter...")
    
    # Initialize the vehicle detector/tracker
    try:
        vehicle_counter = VehicleCounter()
        print("Vehicle detection model loaded successfully.")
    except Exception as e:
        print(f"Error initializing vehicle detection model: {e}")
        return
    
    # Video setup
    # video_path = 'C:/Users/Piyush/Desktop/Personal Work/DEKHO/backend/data/test1.mp4'
    # print(f"Opening video: {video_path}")
    
    # if not os.path.exists(video_path):
    #     print("Error: Video file does not exist")
    #     return
    
    # cap = cv2.VideoCapture(video_path)
    # if not cap.isOpened():
    #     print("Error: Could not open video")
    #     return

    # Webcam setup
    webcam_index = 1  # Use 0 for the default webcam; change if needed (e.g., 1 for a second camera)
    print(f"Opening webcam with index: {webcam_index}")
    
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Get the first frame to set up ROI
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read first frame")
        return
    
    # Frame dimensions
    frame_height, frame_width = frame.shape[:2]
    print(f"Video dimensions: {frame_width}x{frame_height}")
    
    # Define ROI - modify these coordinates based on your area of interest
    roi_points = [
        (int(frame_width * 0.2), int(frame_height * 0.4)),  # Top-left
        (int(frame_width * 0.8), int(frame_height * 0.4)),  # Top-right
        (int(frame_width * 0.8), int(frame_height * 0.9)),  # Bottom-right
        (int(frame_width * 0.2), int(frame_height * 0.9))   # Bottom-left
    ]
    
    # Initialize area counter
    area_counter = AreaVehicleCounter(roi_points)
    print("Area vehicle counter initialized.")
    
    # Reset video to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Main processing loop
    frame_count = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % 10 == 0:  # Status update every 10 frames
                print(f"Processing frame {frame_count}")
            
            # Process frame for vehicle detection and tracking
            try:
                tracks = vehicle_counter.process_frame(frame)
            except Exception as e:
                print(f"Error processing frame: {e}")
                # Draw ROI even if detection fails
                area_counter.draw_visualization(frame)
                cv2.imshow('Traffic Density Monitor', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Update area vehicle counter
            count, density = area_counter.update(tracks, frame.shape)
            
            # Draw visualizations
            area_counter.draw_visualization(frame)
            
            # Draw bounding boxes for vehicles in ROI
            for track in tracks:
                if len(track) < 5:
                    continue
                    
                try:
                    x1, y1, x2, y2 = map(int, track[0:4])
                    track_id = int(track[4])
                    
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    # Different color for vehicles in ROI
                    in_roi = area_counter.is_in_roi((center_x, center_y))
                    color = (0, 255, 0) if in_roi else (0, 0, 255)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw ID
                    cv2.putText(frame, f"{track_id}", (x1, y1-5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                except Exception as e:
                    # Skip problematic tracks
                    continue
            
            # Display statistics
            cv2.putText(frame, f"Vehicles in ROI: {count}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Density: {density:.1f}%", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('Traffic Density Monitor', frame)
            
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Processing interrupted by user")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("Process completed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {e}")