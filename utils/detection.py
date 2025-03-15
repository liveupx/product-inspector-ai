import cv2
import numpy as np
import time
import random

class ProductDetector:
    """
    Class for product detection and quality assessment
    """
    def __init__(self, threshold=0.5):
        """
        Initialize the product detector
        Args:
            threshold: Detection confidence threshold
        """
        self.threshold = threshold
        self.last_detection_id = 0
        # Tracking dictionary to avoid duplicate detections
        self.tracked_objects = {}
        
        # Load detection models
        # In a real implementation, this would load actual ML models
        self.initialize_models()
        
    def initialize_models(self):
        """
        Initialize detection models 
        In an actual implementation, this would load real models
        """
        # Placeholder for model initialization
        # For demo purposes, we'll simulate detection
        pass
        
    def set_threshold(self, threshold):
        """Set detection threshold"""
        self.threshold = threshold
        
    def detect_products(self, frame):
        """
        Detect products in the frame
        Args:
            frame: Input image frame
        Returns:
            List of detected products with their properties
        """
        # In a real implementation, this would use an object detection model
        # For demo purposes, we'll simulate detection
        
        # Convert frame to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply some basic image processing
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
        
        # Find contours in the image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        # Filter contours by size to find potential products
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Minimum size threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Assign a unique ID to each detection
                self.last_detection_id += 1
                detection_id = self.last_detection_id
                
                # Determine quality (good or bad)
                # In a real system, this would use an ML model
                # For demo, randomly assign with bias toward "good"
                quality_score = random.random()
                quality = 'good' if quality_score > 0.3 else 'bad'
                
                detections.append({
                    'id': detection_id,
                    'bbox': (x, y, w, h),
                    'confidence': random.uniform(0.7, 0.98),
                    'quality': quality,
                    'quality_score': quality_score
                })
        
        return detections
    
    def process_frame(self, frame, draw_results=True):
        """
        Process a frame: detect products and optionally visualize results
        Args:
            frame: Input image frame
            draw_results: Whether to draw detection results on the frame
        Returns:
            Processed frame and list of detections
        """
        # Create a copy of the frame for drawing
        result_frame = frame.copy()
        
        # Detect products
        detections = self.detect_products(frame)
        
        # Filter by threshold
        detections = [d for d in detections if d['confidence'] >= self.threshold]
        
        if draw_results and detections:
            # Draw bounding boxes and labels
            for detection in detections:
                x, y, w, h = detection['bbox']
                
                # Choose color based on quality
                if detection['quality'] == 'good':
                    color = (0, 255, 0)  # Green for good products
                else:
                    color = (0, 0, 255)  # Red for defective products
                
                # Draw bounding box
                cv2.rectangle(result_frame, (x, y), (x+w, y+h), color, 2)
                
                # Add label with ID and confidence
                label = f"{detection['id']} {detection['quality']} {detection['confidence']:.2f}"
                cv2.putText(result_frame, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
            # Add processing info
            processing_info = f"Objects: {len(detections)}"
            cv2.putText(result_frame, processing_info, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return result_frame, detections
    
    def analyze_product_quality(self, product_image):
        """
        Analyze a single product for quality issues
        Args:
            product_image: Cropped image of a single product
        Returns:
            Quality assessment results
        """
        # In a real implementation, this would use specialized ML models
        # For demo purposes, we'll return simulated results
        
        defects = []
        if random.random() < 0.3:
            possible_defects = ["scratch", "dent", "discoloration", "misalignment", "missing_label"]
            num_defects = random.randint(0, 2)
            defects = random.sample(possible_defects, num_defects)
        
        quality_score = random.uniform(0.7, 1.0) if not defects else random.uniform(0.3, 0.7)
        
        return {
            'quality': 'good' if quality_score > 0.7 else 'bad',
            'score': quality_score,
            'defects': defects
        }
