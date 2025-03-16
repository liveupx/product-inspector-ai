import cv2
import numpy as np
import time
import random
import math

def create_water_bottle(frame_shape, position=None, quality='good'):
    """Create a synthetic water bottle image
    
    Args:
        frame_shape: Shape of the target frame (height, width)
        position: (x,y) position where to place the bottle
        quality: 'good' or 'bad' to simulate defects
        
    Returns:
        Mask and bottle image to overlay
    """
    h, w = frame_shape[:2]
    
    # If position is not provided, use random position
    if position is None:
        x = random.randint(w//4, 3*w//4)
        y = random.randint(h//4, 3*h//4)
    else:
        x, y = position
    
    # Create bottle shape
    bottle_h, bottle_w = 300, 120
    bottle = np.zeros((bottle_h, bottle_w, 4), dtype=np.uint8)
    
    # Draw bottle body
    cv2.rectangle(bottle, (30, 50), (bottle_w-30, bottle_h-70), (200, 200, 200, 230), -1)
    
    # Draw bottle neck
    cv2.rectangle(bottle, (45, 10), (bottle_w-45, 50), (200, 200, 200, 230), -1)
    
    # Draw bottle cap
    cap_color = (0, 0, 255, 255) if random.random() < 0.5 else (0, 0, 200, 255)
    cv2.rectangle(bottle, (40, 0), (bottle_w-40, 20), cap_color, -1)
    
    # Add label
    label_y = bottle_h - 120
    cv2.rectangle(bottle, (20, label_y), (bottle_w-20, bottle_h-20), (255, 255, 255, 200), -1)
    
    # Add water level
    water_level = random.randint(100, 200)
    cv2.rectangle(bottle, (30, water_level), (bottle_w-30, bottle_h-70), (64, 164, 223, 128), -1)
    
    # Simulate defects for bad bottles
    if quality == 'bad':
        defect_type = random.choice(['dent', 'label', 'cap'])
        
        if defect_type == 'dent':
            # Add a dent to the bottle
            dent_x = random.randint(30, bottle_w-30)
            dent_y = random.randint(70, bottle_h-100)
            cv2.circle(bottle, (dent_x, dent_y), 20, (0, 0, 0, 0), -1)
        
        elif defect_type == 'label':
            # Crooked label
            M = cv2.getRotationMatrix2D((bottle_w//2, label_y + 50), random.uniform(10, 20), 1.0)
            label_mask = np.zeros_like(bottle)
            cv2.rectangle(label_mask, (20, label_y), (bottle_w-20, bottle_h-20), (255, 255, 255, 255), -1)
            rotated_mask = cv2.warpAffine(label_mask, M, (bottle_w, bottle_h))
            
            # Apply rotated mask
            bottle_without_label = bottle.copy()
            cv2.rectangle(bottle_without_label, (20, label_y), (bottle_w-20, bottle_h-20), (0, 0, 0, 0), -1)
            
            # Add rotated label
            for c in range(4):
                bottle[:,:,c] = np.where(rotated_mask[:,:,c] > 0, 
                                         np.maximum(bottle[:,:,c], rotated_mask[:,:,c]), 
                                         bottle_without_label[:,:,c])
        
        elif defect_type == 'cap':
            # Missing or damaged cap
            cv2.rectangle(bottle, (40, 0), (bottle_w-40, 20), (0, 0, 0, 0), -1)
    
    # Calculate bounding box on target frame
    x1 = max(0, x - bottle_w//2)
    y1 = max(0, y - bottle_h//2)
    x2 = min(w, x + bottle_w//2)
    y2 = min(h, y + bottle_h//2)
    
    return bottle, (x1, y1, x2-x1, y2-y1)

def get_demo_frame(frame_size=(720, 1280, 3), show_detection=True):
    """Generate a demo frame simulating a production line with bottles
    
    Args:
        frame_size: Size of the frame to generate
        show_detection: Whether to show detection visualization
        
    Returns:
        Demo frame with bottles
    """
    h, w = frame_size[:2]
    
    # Create background (conveyor belt)
    frame = np.ones((h, w, 3), dtype=np.uint8) * 80
    
    # Add conveyor belt texture
    for i in range(0, h, 20):
        cv2.line(frame, (0, i), (w, i), (60, 60, 60), 1)
    
    # Add side rails
    cv2.rectangle(frame, (0, h//3), (w, h//3 + 10), (100, 100, 100), -1)
    cv2.rectangle(frame, (0, 2*h//3), (w, 2*h//3 + 10), (100, 100, 100), -1)
    
    # Decide how many bottles to show (1-3)
    num_bottles = random.randint(1, 3)
    bottles_info = []
    
    # Generate bottle positions
    for i in range(num_bottles):
        x = w // (num_bottles + 1) * (i + 1)
        y = h // 2
        
        # Randomly determine quality
        quality = 'good' if random.random() < 0.8 else 'bad'
        
        # Create bottle image
        bottle_img, bbox = create_water_bottle((h, w), (x, y), quality)
        bottles_info.append({
            'id': 30 + i,
            'bbox': bbox,
            'quality': quality,
            'confidence': random.uniform(0.8, 0.99),
            'bottle_img': bottle_img
        })
    
    # Add bottles to frame
    for bottle_info in bottles_info:
        x, y, bottle_w, bottle_h = bottle_info['bbox']
        bottle_img = bottle_info['bottle_img']
        
        # Extract region of interest
        roi = frame[y:y+bottle_h, x:x+bottle_w]
        
        # Only modify the frame where bottle is not transparent
        for c in range(3):
            roi[:,:,c] = np.where(bottle_img[:,:,3] > 0, 
                               ((bottle_img[:,:,c] * bottle_img[:,:,3] // 255) + 
                                (roi[:,:,c] * (255 - bottle_img[:,:,3]) // 255)), 
                               roi[:,:,c])
    
    # Add detection visualization
    if show_detection:
        for bottle_info in bottles_info:
            x, y, w, h = bottle_info['bbox']
            quality = bottle_info['quality']
            confidence = bottle_info['confidence']
            bottle_id = bottle_info['id']
            
            # Choose color based on quality
            color = (0, 255, 0) if quality == 'good' else (0, 0, 255)
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Add ID and class label
            bottle_label = f"{bottle_id} {quality}"
            cv2.putText(frame, bottle_label, (x, y-10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Add confidence score
            conf_label = f"{confidence:.2f}"
            cv2.putText(frame, conf_label, (x, y+h+20), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Add timestamp and frame info
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Add processing info overlay
    if show_detection:
        overlay = np.ones((140, 250, 3), dtype=np.uint8) * 50
        cv2.putText(overlay, "defect_recognition", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(overlay, f"Speed: {random.uniform(1.0, 3.0):.1f}ms preprocess", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        for i, bottle_info in enumerate(bottles_info):
            y_pos = 60 + i * 20
            bottle_id = bottle_info['id']
            quality = bottle_info['quality']
            cv2.putText(overlay, f"Object ID:  {bottle_id}", (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(overlay, f"Class:  {quality}", (10, y_pos + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Place overlay on frame
        frame[10:10+overlay.shape[0], 10:10+overlay.shape[1]] = overlay
    
    return frame