

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Object Detector Module

This module is responsible for detecting cricket-related objects in video frames,
including the ball, stumps, batsman, and bat. It uses a combination of traditional
computer vision techniques and deep learning approaches.

Team Member Responsibilities:
----------------------------
Member 3: Object detection implementation, model training/integration, and detection optimization
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple

class ObjectDetector:
    """
    Detects cricket-related objects in frames.
    
    This class implements detection algorithms for cricket balls, stumps,
    batsmen, and bats.
    
    Team Member Responsibilities:
    ----------------------------
    All Members made combined effort :)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Object Detector with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.detection_method = config.get("detection_method", "hybrid")
        self.confidence_threshold = config.get("confidence_threshold", 0.5)
        
        # Initialize detection models based on method
        #if self.detection_method in ["deep_learning", "hybrid"]:
        #    self._init_deep_learning_models()
        
        # Initialize traditional CV parameters
        self._init_traditional_cv_params()
    
    
       
    def _init_traditional_cv_params(self):
        """Initialize parameters for traditional computer vision approaches."""
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

        
        ball_detections = self._detect_ball_traditional(frame)
        results["ball"] = ball_detections
        
        # Detect stumps 
        stump_detections = self._detect_stumps_traditional(frame)
       
        results["stumps"] = stump_detections
        batsman_detections = self._detect_batsman_traditional(frame)
        
        frame_resized = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rects, weights = self.hog.detectMultiScale(
            frame_resized,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )

        detections = []
        frame_width = frame.shape[1]

        for (x, y, w, h), weight in zip(rects, weights):
            if weight >= self.confidence_threshold:
               
                x, y, w, h = int(x * 2), int(y * 2), int(w * 2), int(h * 2)
                center_x = x + w // 2

            
                if 0.2 * frame_width < center_x < 0.8 * frame_width:
                   
                    shrink_factor = 0.7
                    new_w = int(w * shrink_factor)
                    new_h = int(h * shrink_factor)
                    new_x = x + (w - new_w) // 2
                    new_y = y + (h - new_h) // 2

                    detections.append({
                        "bbox": (new_x, new_y, new_w, new_h),
                        "confidence": float(weight)
                    })

        results["batsman"] = detections
         

    def _detect_batsman_traditional(self, frame: np.ndarray) -> List[Dict[str, Any]]:
     
        frame_resized = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

   
        rects, weights = self.hog.detectMultiScale(
            frame_resized,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )

        detections = []
        frame_width = frame.shape[1]

        for (x, y, w, h), weight in zip(rects, weights):
            if weight >= self.confidence_threshold:
             
                x, y, w, h = int(x * 2), int(y * 2), int(w * 2), int(h * 2)
                center_x = x + w // 2
                if 0.2 * frame_width < center_x < 0.8 * frame_width:
                    shrink = 0.7
                    new_w = int(w * shrink)
                    new_h = int(h * shrink)
                    new_x = x + (w - new_w) // 2
                    new_y = y + (h - new_h) // 2

                    detections.append({
                        "bbox": [new_x, new_y, new_w, new_h],
                        "confidence": float(weight)
                    })

        return detections    

    def _detect_ball_traditional(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect cricket ball using traditional CV techniques.
        
        Args:
            frame: Input frame
            
        Returns:
            List of ball detection results
        """
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
        """
        Detect stumps using traditional CV techniques.
        
        Args:
            frame: Input frame
            
        Returns:
            List of stump detection results
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # stumps
        lower = np.array([10,  80,  80], dtype=np.uint8)   # H:5–35, S:60–255, V:60–255
        upper = np.array([40, 255, 255], dtype=np.uint8)
        mask  = cv2.inRange(hsv, lower, upper)

        # 3) clean up noise
        # kernel = np.ones((5,5), np.uint8)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        #  # **DEBUG: show mask side‑by‑side**
        # cv2.imshow("frame", frame)
        # cv2.imshow("stump_mask", mask)
        # cv2.waitKey(1)   

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
    
    def _init_deep_learning_models(self):
        return