#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stump Detector Module

Detects the full wicket in a frame as one bounding box, tracking its 3D position.
Falls back to pad-based inference when stumps are occluded by the batsman.
"""
import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class StumpTracker:
    def __init__(self, config: Dict[str, Any]):
        self.min_detection_confidence = config.get("min_detection_confidence", 0.5)
        self.focal_length = config.get("focal_length_pixels", 1500)
        self.real_stump_height = config.get("stump_height", 0.71)  # meters
        # HSV range for white/cream stumps
        self.stump_color_lower = np.array([0, 0, 200], dtype=np.uint8)
        self.stump_color_upper = np.array([180, 20, 255], dtype=np.uint8)

    def track(
        self,
        frame: np.ndarray,
        pads: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Args:
          frame: input image
          pads: optional list of pad detections (each with 'bbox': (x,y,w,h))

        Returns:
          A single dict with keys:
            'bbox': (x, y, w, h),
            'confidence': float,
            'position': {'x': float, 'y': float, 'z': float}
          or None if neither stumps nor pads available.
        """
        # 1) Try direct stump detection
        stump_list = self._detect_stumps_traditional(frame)
        if stump_list:
            return self._merge_and_output(stump_list, frame)

        # 2) Fallback: infer from pads
        if pads:
            # union of pad boxes
            xs = [p['bbox'][0] for p in pads]
            ys = [p['bbox'][1] for p in pads]
            ws = [p['bbox'][2] for p in pads]
            hs = [p['bbox'][3] for p in pads]
            x_min = min(xs)
            x_max = max(x + w for x, w in zip(xs, ws))
            w_box = x_max - x_min
            # wicket height approx twice pad height in pixels
            max_pad_h = max(hs)
            h_box = int(min(max_pad_h * 2, frame.shape[0]))
            y_max = max(y + h for y, h in zip(ys, hs))
            y_min = max(0, y_max - h_box)
            bbox = (int(x_min), int(y_min), int(w_box), int(h_box))
            # low confidence since inferred
            stub = [{'bbox': bbox, 'confidence': 0.0}]
            return self._merge_and_output(stub, frame)

        # nothing to return
        return None

    def _merge_and_output(
        self,
        stumps: List[Dict[str, Any]],
        frame: np.ndarray
    ) -> Dict[str, Any]:
        # merge all bboxes into one
        xs = [d['bbox'][0] for d in stumps]
        ys = [d['bbox'][1] for d in stumps]
        ws = [d['bbox'][2] for d in stumps]
        hs = [d['bbox'][3] for d in stumps]
        x_min = min(xs)
        y_min = min(ys)
        x_max = max(x + w for x, w in zip(xs, ws))
        y_max = max(y + h for y, h in zip(ys, hs))
        bbox = (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))
        conf = max(d['confidence'] for d in stumps)
        # 3D position at base center
        bottom = (x_min + bbox[2] / 2, y_min + bbox[3])
        pos = self._estimate_point_3d(bottom, frame.shape[:2])
        return {
            'bbox': bbox,
            'confidence': float(conf),
            'position': {'x': round(pos[0], 3), 'y': round(pos[1], 3), 'z': round(pos[2], 3)}
        }

    def _detect_stumps_traditional(
        self,
        frame: np.ndarray
    ) -> List[Dict[str, Any]]:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.stump_color_lower, self.stump_color_upper)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        h_img, w_img = frame.shape[:2]
        detections: List[Dict[str, Any]] = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h > 50 and (h / float(w) if w else 0) > 2.5:
                z = (self.focal_length * self.real_stump_height) / (h + 1e-6)
                cx = x + w / 2
                x_norm = (cx - w_img / 2) / (w_img / 2)
                x_world = x_norm * z
                detections.append({
                    'bbox': (x, y, w, h),
                    'confidence': 1.0,
                    'position': {'x': x_world, 'y': 0.0, 'z': z}
                })
        return detections

    def _estimate_point_3d(
        self,
        point: Tuple[float, float],
        frame_dim: Tuple[int, int]
    ) -> np.ndarray:
        x_img, y_img = point
        width, height = frame_dim[1], frame_dim[0]
        x_norm = (x_img - width / 2) / (width / 2)
        z = (self.focal_length * self.real_stump_height) / (height + 1e-6)
        x_w = x_norm * z
        return np.array([x_w, 0.0, z])
