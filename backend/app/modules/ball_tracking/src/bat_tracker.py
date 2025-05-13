#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bat Tracker Module

Detects the cricket bat in a frame using color thresholding around the batsman region.
Falls back to using batsman keypoints (wrist, elbow) to infer bat location if color detection fails.
Calculates approximate 3D position (x,y,z) of the bat via pinhole model.
"""
import cv2
import numpy as np
from typing import Dict, List, Any, Tuple

class BatTracker:
    def __init__(self, config: Dict[str, Any]):
        # HSV range for bat color (wooden tones)
        self.bat_color_lower = np.array(config.get("bat_color_lower", [10, 50, 50]), dtype=np.uint8)
        self.bat_color_upper = np.array(config.get("bat_color_upper", [30, 255, 255]), dtype=np.uint8)
        self.min_contour_area = config.get("min_contour_area", 500)
        # real bat length in meters (approx)
        self.real_bat_length = config.get("real_bat_length", 0.96)
        self.focal_length = config.get("focal_length_pixels", 1500)
        self.arm_keypoints = ["Left Wrist", "Right Wrist", "Left Elbow", "Right Elbow"]

    def track(
        self,
        frame: np.ndarray,
        batsman_detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        
        detections: List[Dict[str, Any]] = []

        # 1) Color-based detection (unchanged)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.bat_color_lower, self.bat_color_upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for batsman in batsman_detections:
            x_b, y_b, w_b, h_b = batsman.get("bbox", (0,0,0,0))
            roi = (max(0, x_b-20), max(0, y_b-20), w_b+40, h_b+40)
            for cnt in contours:
                if cv2.contourArea(cnt) < self.min_contour_area:
                    continue
                x,y,w,h = cv2.boundingRect(cnt)
                if (x >= roi[0] and y >= roi[1]
                    and x+w <= roi[0]+roi[2] and y+h <= roi[1]+roi[3]
                    and h/float(w) > 2.0):
                    det = {"bbox": (x,y,w,h), "confidence": 1.0}
                    det["position"] = self._estimate_3d((x,y,w,h), frame.shape)
                    detections.append(det)

        if detections:
            return detections

        # 2) Fallback: try multiple keypoint pairs
        h_img, w_img = frame.shape[:2]
        for batsman in batsman_detections:
            pose = batsman.get("pose", {})
            # priority-ordered pairs
            pairs = [
                ("Left Wrist",    "Left Elbow"),
                ("Right Wrist",   "Right Elbow"),
                ("Left Elbow",    "Left Shoulder"),
                ("Right Elbow",   "Right Shoulder"),
            ]
            for a, b in pairs:
                p1, p2 = pose.get(a), pose.get(b)
                if p1 and p2:
                    break
            else:
                continue  # no usable pair found

            dx, dy = p1[0] - p2[0], p1[1] - p2[1]
            length = np.hypot(dx, dy)
            if length < 1e-3:
                continue

            # unit vector and extension
            ux, uy = dx/length, dy/length
            ext = int(length)
            ex, ey = int(p1[0] + ux*ext), int(p1[1] + uy*ext)

            xs = [p2[0], p1[0], ex]
            ys = [p2[1], p1[1], ey]
            x_min = max(0, min(xs)-5)
            y_min = max(0, min(ys)-5)
            x_max = min(w_img, max(xs)+5)
            y_max = min(h_img, max(ys)+5)

            w_rect, h_rect = x_max - x_min, y_max - y_min
            # ensure plausible bat shape (tall rectangle)
            if h_rect / (w_rect + 1e-6) < 1.5:
                continue

            det = {
                "bbox":       (x_min, y_min, w_rect, h_rect),
                "confidence": 0.5
            }
            det["position"] = self._estimate_3d((x_min, y_min, w_rect, h_rect), frame.shape)
            detections.append(det)

        return detections


    def _estimate_3d(
        self,
        bbox: Tuple[int,int,int,int],
        frame_shape: Tuple[int,int,int]
    ) -> Dict[str, float]:
        """
        Estimates 3D world position of the bat's center using pinhole camera model.
        """
        x, y, w, h = bbox
        cx, cy = x + w/2, y + h/2
        fh, fw = frame_shape[0], frame_shape[1]
        x_norm = (cx - fw/2) / (fw/2)
        # depth based on observed bat length in image
        z = (self.focal_length * self.real_bat_length) / (h + 1e-6)
        x_w = x_norm * z
        y_w = 0.0
        return {"x": round(x_w,3), "y": round(y_w,3), "z": round(z,3)}
