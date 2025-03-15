import cv2
import numpy as np
import time
import streamlit as st
from threading import Thread

class VideoCapture:
    """
    Class to handle video capture from various sources
    with threading for better performance
    """
    def __init__(self, source=0):
        """
        Initialize the video capture
        Args:
            source: Camera index or video file path
        """
        self.source = source
        self.cap = None
        self.thread = None
        self.stopped = False
        self.frame = None
        self.last_frame_time = 0
        self.fps = 0
        
    def start(self):
        """Start the video capture thread"""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source {self.source}")
            
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Start thread
        self.stopped = False
        self.thread = Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def _update(self):
        """Read frames continuously from the camera"""
        while not self.stopped:
            if self.cap is not None:
                ret, frame = self.cap.read()
                if ret:
                    current_time = time.time()
                    if self.last_frame_time > 0:
                        self.fps = 1 / (current_time - self.last_frame_time)
                    self.last_frame_time = current_time
                    
                    self.frame = frame
                else:
                    # If we reach the end of a video file, loop back
                    if isinstance(self.source, str):
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        self.stop()
                        break
            time.sleep(0.01)  # Small delay to reduce CPU usage
    
    def read(self):
        """Return the most recent frame"""
        return self.frame
    
    def get_fps(self):
        """Return the fps of the video capture"""
        return self.fps
    
    def stop(self):
        """Stop the video capture thread"""
        self.stopped = True
        if self.thread is not None:
            self.thread.join()
        if self.cap is not None:
            self.cap.release()
            
    def __del__(self):
        """Cleanup on object destruction"""
        self.stop()
