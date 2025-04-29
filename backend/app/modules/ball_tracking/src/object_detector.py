#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Object Detector Module

This module is responsible for detecting cricket-related objects in video frames,
including the ball, stumps, batsman, and bat. Support for Deep Learning may be added later.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple

class ObjectDetector:
    """
    All Members made combined effort :)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Object Detector with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.detection_method = config.get("detection_method", "traditional")
        self.confidence_threshold = config.get("confidence_threshold", 0.5)
        
        
        
        # Initialize traditional CV parameters
        self._init_traditional_cv_params()
    
    
       
    def _init_traditional_cv_params(self):
        # tuned for yellow ball
        self.ball_color_lower = np.array([30,150,150], dtype=np.uint8)
        self.ball_color_upper = np.array([40,255,255], dtype=np.uint8)
        self.min_ball_radius   = 5
        
        # Stump detection parameters
        self.stump_color_lower = np.array([0, 0, 200])  # HSV lower bound for white/cream stumps
        self.stump_color_upper = np.array([180, 20, 255])  # HSV upper bound for white/cream stumps
        
        # Initialize background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=self.config.get("bg_history", 120),
            varThreshold=self.config.get("bg_threshold", 16)
        )
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    
    def isolate_objects(self, frame):
        """
        Isolate ball and stumps from the frame using color filtering.
        """
        # Convert frame to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create ball mask
        ball_mask = cv2.inRange(hsv, self.ball_color_lower, self.ball_color_upper)

        # Create stump mask
        stump_mask = cv2.inRange(hsv, self.stump_color_lower, self.stump_color_upper)

        # Combine masks
        combined_mask = cv2.bitwise_or(ball_mask, stump_mask)

        # Apply the mask to the frame
        result = cv2.bitwise_and(frame, frame, mask=combined_mask)

        return result, combined_mask
    
    def detect(self, frame: np.ndarray) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect objects in the frame.
        Args:
            frame: Input frame as numpy array            
        Returns:
            Dictionary containing detection results for each object type
        """
        results = {
            "ball": [],
            "stumps": [],
            "batsman": [],
            "bat": []
        }
        
        # Choose detection method based on configuration
        self._detect_with_traditional_cv(frame, results)

        return results
    
    
    def _detect_with_traditional_cv(self, frame: np.ndarray, results: Dict[str, List[Dict[str, Any]]]):
        """
        Detect objects using traditional computer vision techniques.
        
        Args:
            frame: Input frame
            results: Dictionary to store detection results
        """
        # Detect ball using color and shape
        ball_detections = self._detect_ball_traditional(frame)
        results["ball"] = ball_detections
        
        # Detect stumps 
        stump_detections = self._detect_stumps_traditional(frame)
       
        results["stumps"] = stump_detections

    def _detect_ball_traditional(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,
                        self.ball_color_lower,
                        self.ball_color_upper)
        mask = cv2.erode( mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask,
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        balls = []
        if contours:
            c = max(contours, key=cv2.contourArea)
            (x,y), radius = cv2.minEnclosingCircle(c)
            if radius > self.min_ball_radius:
                balls.append({
                "bbox":       (int(x-radius), int(y-radius),
                                int(2*radius),  int(2*radius)),
                "confidence": 1.0,
                "center":     (int(x), int(y)),
                "radius":     int(radius)
                })
        return balls
    
    def _detect_stumps_traditional(self, frame: np.ndarray) -> List[Dict[str, Any]]:

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # stumps
        lower = np.array([10,  80,  80], dtype=np.uint8)   # H:5–35, S:60–255, V:60–255
        upper = np.array([40, 255, 255], dtype=np.uint8)
        mask  = cv2.inRange(hsv, lower, upper)

        contours, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        stumps = []
        for c in contours:
            x,y,w,h = cv2.boundingRect(c)
            aspect = h / float(w) if w>0 else 0

            # only keep nice tall thin pieces
            if h > 75 and aspect > 3.0: 
                stumps.append({
                    "bbox":       (x, y, w, h),
                    "confidence": 1.0,
                    "top":        (x + w//2, y),
                    "bottom":     (x + w//2, y + h)
                })

        return stumps
