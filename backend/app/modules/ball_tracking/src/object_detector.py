

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Object Detector Module

This module is responsible for detecting cricket-related objects in video frames,
including the ball, stumps, batsman, and bat.

"""

import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import time
from typing import Dict, List, Any, Tuple
from ball_tracker import BallTracker
from batsman_tracker import BatsmanTracker
from stump_tracker import StumpTracker
from bat_tracker import BatTracker

class ObjectDetector:    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Object Detector with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
    
        self.ball_history: List[Dict[str,Any]] = []
        self.ball_tracker = BallTracker(self.config)
        
        self.batsman_tracker = BatsmanTracker(self.config)
        
        self.stump_tracker = StumpTracker(self.config)
        
        self.bat_tracker = BatTracker(self.config)
    
       
    def detect(self, frame: np.ndarray) -> Dict[str, List[Dict[str, Any]]]:
        results = {"ball": [], "stumps": [], "batsman": [], "bat": [], "pads": []}

        # Detect objects
        
        traj = self.ball_tracker.track(frame, historical_positions=self.ball_history)
        if traj:
            simple_pt = traj["current_position"]
            self.ball_history.append(simple_pt)  
            results["ball"] = [traj]
        else:
            results["ball"] = []

        batsman_track, pads_track = self.batsman_tracker.track(frame)
        results["batsman"] = [
            {
                "bbox":        det["bbox"],
                "confidence":  round(det["confidence"], 3),
                "position":    det["position"]
            }
            for det in batsman_track
        ]
        results["pads"] = pads_track
        
        stump = self.stump_tracker.track(frame, results["pads"])
        results["stumps"] = [stump] if stump else []

        bat_track = self.bat_tracker.track(frame, batsman_track)
        results["bat"] = bat_track
        
        return results
    