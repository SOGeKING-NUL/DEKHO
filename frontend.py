import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import tempfile
from main import TrafficSimulator, main as run_simulation
from mainn1 import main as run_webcam_analysis
from main2 import process_video

# Custom CSS for modern styling
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 25px;
        padding: 12px 28px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .sidebar .sidebar-content {
        background-color: #2D2D2D;
    }
    h1, h2, h3 {
        color: #4CAF50 !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🚦 Smart Traffic Management System")
    st.markdown("### Integrated Traffic Monitoring & Control Dashboard")

    # Navigation
    app_mode = st.sidebar.selectbox("Choose Module", 
                                   ["🏠 Home", "🛣️ Traffic Simulation", "📷 Live Webcam Analysis", "📹 Video Processing"])

    if app_mode == "🏠 Home":
        show_home()
    elif app_mode == "🛣️ Traffic Simulation":
        run_simulation_module()
    elif app_mode == "📷 Live Webcam Analysis":
        run_webcam_module()
    elif app_mode == "📹 Video Processing":
        run_video_processing_module()

def show_home():
    st.markdown("""
    ## Welcome to DEKHO Traffic Analytics
    **Monitor and manage traffic flow with AI-powered insights**
    
    ### Features:
    - Real-time traffic simulation
    - Live webcam analysis
    - Historical video processing
    - Vehicle counting & classification
    - Adaptive traffic light control
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Vehicles Tracked", "1,234", "+12%")
    with col2:
        st.metric("Average Wait Time", "45s", "-8%")
    with col3:
        st.metric("Traffic Efficiency", "82%", "+5%")

def run_simulation_module():
    st.header("Traffic Light Simulation")
    if st.button("Start Simulation"):
        with st.spinner("Running traffic simulation..."):
            video_path = 'simulation_output.mp4'
            run_simulation()  # Modify your main.py to save output
            
            show_video(video_path, "Simulation Results")

def run_webcam_module():
    st.header("Live Webcam Analysis")
    if st.button("Start Webcam Feed"):
        st.warning("Ensure webcam is connected")
        webcam_placeholder = st.empty()
        run_webcam_analysis(source=0)  # Modify mainn1.py to yield frames

def run_video_processing_module():
    st.header("Video Processing")
    uploaded_file = st.file_uploader("Upload Traffic Video", type=["mp4", "avi"])
    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Video")
            show_video(tfile.name, "Uploaded Video")
        
        with col2:
            st.subheader("Processed Analysis")
            with st.spinner("Analyzing traffic patterns..."):
                process_video(tfile.name)  # Modify main2.py to return frames
                show_video('processed_output.mp4', "Analysis Results")

def show_video(video_path, title):
    video_bytes = open(video_path, 'rb').read()
    st.video(video_bytes, format='video/mp4', start_time=0)

if __name__ == "__main__":
    main()