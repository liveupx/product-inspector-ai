import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import os
import pandas as pd
from utils.camera import VideoCapture
from utils.detection import ProductDetector
from utils.database import InspectionDatabase
from utils.reporting import generate_session_summary

# Set page configuration
st.set_page_config(
    page_title="Product Quality Inspection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'detector' not in st.session_state:
    st.session_state.detector = ProductDetector()
if 'inspection_db' not in st.session_state:
    st.session_state.inspection_db = InspectionDatabase()
if 'product_count' not in st.session_state:
    st.session_state.product_count = {'total': 0, 'good': 0, 'bad': 0}
if 'inspection_active' not in st.session_state:
    st.session_state.inspection_active = False
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = None
if 'current_product_info' not in st.session_state:
    st.session_state.current_product_info = {
        'name': 'Default Product',
        'batch_number': '000001',
        'company': 'Company Name',
        'inspection_criteria': 'Standard'
    }
if 'detection_threshold' not in st.session_state:
    st.session_state.detection_threshold = 0.5
if 'processing_fps' not in st.session_state:
    st.session_state.processing_fps = 0

def toggle_inspection():
    if st.session_state.inspection_active:
        st.session_state.inspection_active = False
        # Generate summary when stopping inspection
        if st.session_state.session_start_time:
            session_duration = (datetime.now() - st.session_state.session_start_time).total_seconds()
            generate_session_summary(
                st.session_state.inspection_db,
                st.session_state.product_count,
                st.session_state.current_product_info,
                session_duration
            )
    else:
        st.session_state.inspection_active = True
        st.session_state.session_start_time = datetime.now()
        st.session_state.product_count = {'total': 0, 'good': 0, 'bad': 0}
        st.session_state.inspection_db.start_new_session(
            st.session_state.current_product_info['name'],
            st.session_state.current_product_info['batch_number']
        )

# Sidebar for controls and settings
with st.sidebar:
    st.title("Control Panel")
    
    st.subheader("Product Information")
    product_name = st.text_input("Product Name", st.session_state.current_product_info['name'])
    batch_number = st.text_input("Batch Number", st.session_state.current_product_info['batch_number'])
    company_name = st.text_input("Company Name", st.session_state.current_product_info['company'])
    
    # Update product info in session state
    if product_name != st.session_state.current_product_info['name'] or \
       batch_number != st.session_state.current_product_info['batch_number'] or \
       company_name != st.session_state.current_product_info['company']:
        st.session_state.current_product_info['name'] = product_name
        st.session_state.current_product_info['batch_number'] = batch_number
        st.session_state.current_product_info['company'] = company_name
    
    st.subheader("Detection Settings")
    detection_threshold = st.slider("Detection Threshold", 0.0, 1.0, st.session_state.detection_threshold, 0.05)
    if detection_threshold != st.session_state.detection_threshold:
        st.session_state.detection_threshold = detection_threshold
        st.session_state.detector.set_threshold(detection_threshold)
    
    st.button(
        "Start Inspection" if not st.session_state.inspection_active else "Stop Inspection",
        on_click=toggle_inspection,
        type="primary"
    )
    
    if st.session_state.inspection_active:
        st.success("Inspection in progress")
        if st.session_state.session_start_time:
            elapsed_time = (datetime.now() - st.session_state.session_start_time).total_seconds()
            st.write(f"Session duration: {int(elapsed_time // 60)}m {int(elapsed_time % 60)}s")
    else:
        st.warning("Inspection not active")
    
    st.subheader("Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/product_setup.py", label="Product Setup", icon="⚙️")
    st.page_link("pages/reports.py", label="Reports", icon="📝")

# Main content
st.title("Product Quality Inspection System")

col1, col2 = st.columns([3, 1])

with col1:
    # Camera feed container
    video_container = st.empty()
    
    # Placeholder for demo mode or camera selection
    camera_source = st.selectbox(
        "Camera Source",
        ["Demo Video", "Camera 0", "Camera 1", "IP Camera"],
        index=0
    )

with col2:
    # Real-time inspection results
    st.subheader("Inspection Statistics")
    
    # Create metrics placeholders
    total_count_metric = st.empty()
    good_count_metric = st.empty()
    bad_count_metric = st.empty()
    processing_speed_metric = st.empty()
    
    # Product info display
    st.subheader("Current Product")
    product_info_container = st.container()
    
    with product_info_container:
        st.write(f"**Name:** {st.session_state.current_product_info['name']}")
        st.write(f"**Batch:** {st.session_state.current_product_info['batch_number']}")
        st.write(f"**Company:** {st.session_state.current_product_info['company']}")

# Main loop for video processing
# In a real application, this would process the camera feed
if camera_source == "Demo Video":
    # Demo mode using a sample video
    from utils.demo_video import get_demo_frame
    
    while True:
        # Update metrics with current counts
        total_count_metric.metric("Total Products", st.session_state.product_count['total'])
        good_count_metric.metric("Good Products", st.session_state.product_count['good'])
        bad_count_metric.metric("Defective Products", st.session_state.product_count['bad'])
        processing_speed_metric.metric("Processing Speed", f"{st.session_state.processing_fps:.1f} FPS")
        
        if st.session_state.inspection_active:
            # Get a demo frame
            start_time = time.time()
            frame = get_demo_frame()
            
            # Process frame with detector
            processed_frame, detections = st.session_state.detector.process_frame(frame)
            
            # Update product counts based on detections
            if detections:
                new_products = len(detections)
                st.session_state.product_count['total'] += new_products
                
                # Count good and bad products
                good_products = sum(1 for d in detections if d['quality'] == 'good')
                bad_products = new_products - good_products
                
                st.session_state.product_count['good'] += good_products
                st.session_state.product_count['bad'] += bad_products
                
                # Record detections in database
                timestamp = datetime.now()
                for detection in detections:
                    st.session_state.inspection_db.add_inspection_record(
                        product_id=detection['id'],
                        product_name=st.session_state.current_product_info['name'],
                        batch_number=st.session_state.current_product_info['batch_number'],
                        quality=detection['quality'],
                        confidence=detection['confidence'],
                        timestamp=timestamp
                    )
            
            # Calculate processing FPS
            processing_time = time.time() - start_time
            st.session_state.processing_fps = 1.0 / processing_time if processing_time > 0 else 0
            
            # Display the processed frame
            video_container.image(processed_frame, channels="BGR", use_column_width=True)
        else:
            # Just display a placeholder when not active
            frame = get_demo_frame(show_detection=False)
            video_container.image(frame, channels="BGR", use_column_width=True)
        
        # Sleep to simulate real-time processing
        time.sleep(0.1)
else:
    # For actual camera feed (would be implemented in a production system)
    st.warning("Live camera feed not available in this environment. Using demo mode.")
    if not st.session_state.inspection_active:
        from utils.demo_video import get_demo_frame
        frame = get_demo_frame(show_detection=False)
        video_container.image(frame, channels="BGR", use_column_width=True)
