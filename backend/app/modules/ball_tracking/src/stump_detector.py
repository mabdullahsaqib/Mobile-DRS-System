#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stump Detector Module

This module detects cricket stumps as a single wicket bounding box,
tracks its position, and monitors bail status.
"""
import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class StumpDetector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_detection_confidence = config.get("min_detection_confidence", 0.5)
        self.update_interval = config.get("stump_update_interval", 30)  # frames
        self.stump_height_m = config.get("stump_height", 0.71)
        self.stump_spacing = config.get("stump_spacing", 0.11)
        self.max_lost_frames = config.get("max_lost_frames", 10)

        self.last_bbox: Optional[Tuple[int,int,int,int]] = None
        self.last_frame_id = -1
        self.tracking_lost_frames = 0

    def detect(self, frame: np.ndarray, detections: Dict[str, List[Dict[str, Any]]], frame_id: int = 0) -> Dict[str, Any]:
         # Only update every N frames
         if self.last_bbox and (frame_id - self.last_frame_id) < self.update_interval:
             return self._build_output(self.last_bbox, detections)
 
         stumps = detections.get("stumps", [])
         if stumps:
             # merge all stump bboxes into one
             xs = [b[0] for obj in stumps for b in [obj['bbox']]]
             ys = [b[1] for obj in stumps for b in [obj['bbox']]]
             ws = [b[2] for obj in stumps for b in [obj['bbox']]]
             hs = [b[3] for obj in stumps for b in [obj['bbox']]]
             x_min = min(xs)
             y_min = min(ys)
             x_max = max([x + w for x,w in zip(xs, ws)])
             # standardize height to max detected height
             h_std = max(hs)
             bbox = (x_min, y_min, x_max - x_min, h_std)
             self.last_bbox = bbox
             self.last_frame_id = frame_id
             self.tracking_lost_frames = 0
         else:
             # missing detection
             self.tracking_lost_frames += 1
             if self.tracking_lost_frames > self.max_lost_frames or not self.last_bbox:
                 return None
             bbox = self.last_bbox
 
         return self._build_output(bbox, detections)

    def _build_output(self, bbox: Tuple[int,int,int,int], detections: Dict[str, Any]) -> Dict[str, Any]:
        x, y, w, h = bbox
         # bottom-center for 3D estimate
        bottom = (x + w//2, y + h)
        base_center_3d = self._estimate_point_3d_position(bottom, (y+h, x+w))
 
         # single wicket rectangle
        return {
            "position": {"base_center": {"x": base_center_3d[0], "y": base_center_3d[1], "z": base_center_3d[2]}},
            "bbox": {"x": x, "y": y, "w": w, "h": h},
            "detection_confidence": float(max([obj['confidence'] for obj in detections.get('stumps', [])], default=0.0))
         }

    def _estimate_point_3d_position(self, point: Tuple[int,int], frame_shape: Tuple[int,int]) -> np.ndarray:
         # simplified: map pixel to world using fixed depth
        x_img, y_img = point
        width, height = frame_shape[1], frame_shape[0]
        x_norm = (x_img - width/2) / (width/2)
        z = 10.0  # fixed depth
        x_world = x_norm * z
        y_world = 0.0
        return np.array([x_world, y_world, z])
