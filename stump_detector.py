#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stump Detector Module

This module is responsible for detecting and tracking cricket stumps across video frames,
calculating their positions and orientations.

Team Member Responsibilities:
----------------------------
Member 5: Stump detection algorithms, position tracking, and bail status monitoring
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class StumpDetector:
    """
    Detects and tracks cricket stumps across frames.
    
    This class implements algorithms to detect stumps and bails,
    track their positions, and monitor if bails are dislodged.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation of stump detection and tracking algorithms
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Stump Detector with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        
        # Detection parameters
        self.min_detection_confidence = config.get("min_detection_confidence", 0.5)
        self.use_hough_lines = config.get("use_hough_lines", True)
        
        # Stump dimensions (in meters)
        self.stump_height = config.get("stump_height", 0.71)  # Standard cricket stump height
        self.stump_width = config.get("stump_width", 0.038)   # Standard cricket stump width
        self.stump_spacing = config.get("stump_spacing", 0.11)  # Distance between stumps
        
        # State variables
        self.last_stumps_position = None
        self.last_bails_position = None
        self.bails_dislodged = [False, False]  # Status of leg and off bails
        self.tracking_lost_frames = 0
        self.max_lost_frames = config.get("max_lost_frames", 10)
    
    def detect(self, frame: np.ndarray, detections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Detect stumps in the current frame.
        
        Args:
            frame: Current video frame
            detections: Object detection results
            
        Returns:
            Dictionary containing stumps position and status data
        """
        # Extract stumps detections
        stumps_detections = detections.get("stumps", [])
        
        # If no stumps detected
        if not stumps_detections:
            return self._handle_missing_detection(frame)
        
        # Get the most confident stumps detection
        stumps_detection = max(stumps_detections, key=lambda x: x["confidence"])
        
        # Check if confidence is high enough
        if stumps_detection["confidence"] < self.min_detection_confidence:
            return self._handle_missing_detection(frame)
        
        # Extract stumps position
        bbox = stumps_detection["bbox"]
        top = stumps_detection.get("top", (bbox[0] + bbox[2]//2, bbox[1]))
        bottom = stumps_detection.get("bottom", (bbox[0] + bbox[2]//2, bbox[1] + bbox[3]))
        
        # Estimate 3D positions
        base_center_3d = self._estimate_point_3d_position(bottom, frame.shape)
        
        # Calculate individual stump positions
        individual_stumps = self._calculate_individual_stumps(base_center_3d)
        
        # Calculate bail positions and check if dislodged
        bails, bails_dislodged = self._calculate_bails(frame, bbox, individual_stumps)
        
        # Update tracking state
        self.last_stumps_position = base_center_3d
        self.last_bails_position = [bail["position"] for bail in bails]
        self.bails_dislodged = bails_dislodged
        self.tracking_lost_frames = 0
        
        return {
            "position": {
                "base_center": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1]),
                    "z": float(base_center_3d[2])
                }
            },
            "orientation": {
                "pitch": 0.0,  # Assuming stumps are vertical
                "yaw": 0.0,    # Assuming stumps face the camera
                "roll": 0.0    # Assuming no tilt
            },
            "individual_stumps": individual_stumps,
            "bails": bails,
            "detection_confidence": float(stumps_detection["confidence"])
        }
    
    def _handle_missing_detection(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Handle the case when stumps are not detected in the current frame.
        
        Args:
            frame: Current video frame
            
        Returns:
            Estimated stumps data or None
        """
        # Try to detect stumps using traditional CV if deep learning failed
        if self.use_hough_lines:
            stumps_data = self._detect_stumps_traditional(frame)
            if stumps_data:
                return stumps_data
        
        if self.last_stumps_position is None:
            return None
        
        self.tracking_lost_frames += 1
        
        # If tracking is lost for too many frames, reset tracking
        if self.tracking_lost_frames > self.max_lost_frames:
            self.last_stumps_position = None
            return None
        
        # Use last known position with reduced confidence
        confidence = max(0.1, 0.9 - 0.08 * self.tracking_lost_frames)
        
        # Generate stumps data from last known position
        base_center_3d = self.last_stumps_position
        individual_stumps = self._calculate_individual_stumps(base_center_3d)
        
        # Use last known bail status
        bails = [
            {
                "id": "leg_bail",
                "position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] - self.stump_spacing/2)
                },
                "is_dislodged": self.bails_dislodged[0]
            },
            {
                "id": "off_bail",
                "position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] + self.stump_spacing/2)
                },
                "is_dislodged": self.bails_dislodged[1]
            }
        ]
        
        return {
            "position": {
                "base_center": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1]),
                    "z": float(base_center_3d[2])
                }
            },
            "orientation": {
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0
            },
            "individual_stumps": individual_stumps,
            "bails": bails,
            "detection_confidence": float(confidence)
        }
    
    def _detect_stumps_traditional(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Detect stumps using traditional computer vision techniques.
        
        Args:
            frame: Current video frame
            
        Returns:
            Stumps data or None if detection fails
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return None
        
        # Filter vertical lines (potential stumps)
        vertical_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Check if line is approximately vertical
            if abs(x2 - x1) < 20:  # Small horizontal difference
                vertical_lines.append((x1, y1, x2, y2))
        
        if not vertical_lines:
            return None
        
        # Group nearby vertical lines (stumps are usually close together)
        # This is a simplified approach; a real implementation would use clustering
        
        # For simplicity, just use the first set of vertical lines as stumps
        # In a real implementation, this would use more sophisticated grouping
        x_values = [line[0] for line in vertical_lines[:3]]
        y_min = min([min(line[1], line[3]) for line in vertical_lines[:3]])
        y_max = max([max(line[1], line[3]) for line in vertical_lines[:3]])
        
        # Calculate average x position and width
        x_avg = sum(x_values) / len(x_values) if x_values else frame.shape[1] // 2
        width = max(x_values) - min(x_values) + 10 if len(x_values) > 1 else 30  # Add padding
        
        # Create bounding box
        bbox = (int(x_avg - width/2), y_min, int(width), y_max - y_min)
        
        # Estimate 3D position
        bottom = (int(x_avg), y_max)
        base_center_3d = self._estimate_point_3d_position(bottom, frame.shape)
        
        # Calculate individual stump positions
        individual_stumps = self._calculate_individual_stumps(base_center_3d)
        
        # Calculate bail positions (simplified)
        bails = [
            {
                "id": "leg_bail",
                "position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] - self.stump_spacing/2)
                },
                "is_dislodged": False
            },
            {
                "id": "off_bail",
                "position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] + self.stump_spacing/2)
                },
                "is_dislodged": False
            }
        ]
        
        return {
            "position": {
                "base_center": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1]),
                    "z": float(base_center_3d[2])
                }
            },
            "orientation": {
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0
            },
            "individual_stumps": individual_stumps,
            "bails": bails,
            "detection_confidence": 0.7  # Confidence for traditional detection
        }
    
    def _estimate_point_3d_position(self, point: Tuple[int, int], frame_shape: Tuple[int, int, int]) -> np.ndarray:
        """
        Estimate 3D position of a point from 2D coordinates.
        
        Args:
            point: 2D point in the image
            frame_shape: Shape of the frame
            
        Returns:
            Estimated 3D position [x, y, z]
        """
        # Similar to player position estimation but for a single point
        x_image, y_image = point
        height, width = frame_shape[:2]
        
        # Normalize image coordinates to [-1, 1]
        x_norm = (x_image - width/2) / (width/2)
        y_norm = (y_image - height/2) / (height/2)
        
        # Estimate depth (simplified)
        z_depth = 10.0  # Default depth
        
        # Convert to world coordinates (simplified)
        x_world = x_norm * z_depth * 0.5
        y_world = 0.0  # Assume stumps are on the ground
        z_world = -z_depth
        
        return np.array([x_world, y_world, z_world])
    
    def _calculate_individual_stumps(self, base_center_3d: np.ndarray) -> List[Dict[str, Any]]:
        """
        Calculate positions of individual stumps.
        
        Args:
            base_center_3d: 3D position of the base center
            
        Returns:
            List of individual stump data
        """
        # Standard cricket has three stumps: leg, middle, and off
        return [
            {
                "id": "leg",
                "top_position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] - self.stump_spacing)
                }
            },
            {
                "id": "middle",
                "top_position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2])
                }
            },
            {
                "id": "off",
                "top_position": {
                    "x": float(base_center_3d[0]),
                    "y": float(base_center_3d[1] + self.stump_height),
                    "z": float(base_center_3d[2] + self.stump_spacing)
                }
            }
        ]
    
    def _calculate_bails(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                        individual_stumps: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[bool]]:
        """
        Calculate bail positions and check if they are dislodged.
        
        Args:
            frame: Current video frame
            bbox: Bounding box of the stumps
            individual_stumps: List of individual stump data
            
        Returns:
            Tuple of (bails_data, bails_dislodged)
        """
        # In a real implementation, this would analyze the image to detect bails
        # and determine if they are dislodged
        
        # For this prototype, we'll use a simplified approach
        # Extract stumps ROI
        x, y, w, h = bbox
        stumps_roi = frame[y:y+h, x:x+w] if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1] else None
        
        # Default values (assuming bails are in place)
        bails_dislodged = [False, False]
        
        # Get stump top positions
        leg_stump = individual_stumps[0]["top_position"]
        middle_stump = individual_stumps[1]["top_position"]
        off_stump = individual_stumps[2]["top_position"]
        
        # Calculate bail positions (between stumps)
        leg_bail_position = {
            "x": float(leg_stump["x"]),
            "y": float(leg_stump["y"]),
            "z": float((leg_stump["z"] + middle_stump["z"]) / 2)
        }
        
        off_bail_position = {
            "x": float(middle_stump["x"]),
            "y": float(middle_stump["y"]),
            "z": float((middle_stump["z"] + off_stump["z"]) / 2)
        }
        
        bails = [
            {
                "id": "leg_bail",
                "position": leg_bail_position,
                "is_dislodged": bails_dislodged[0]
            },
            {
                "id": "off_bail",
                "position": off_bail_position,
                "is_dislodged": bails_dislodged[1]
            }
        ]
        
        return bails, bails_dislodged
