#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frame Processor Module

Responsibilities:
 - Decode base64-encoded frame data
 - Preprocess frames (resize, noise reduction, contrast enhancement)
 - Provide ROI extraction and encoding utilities
"""
import cv2
import numpy as np
import base64
from typing import Tuple, Optional, Dict, Any

class FrameProcessor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional configuration.
        config keys:
          - target_size: Tuple[int,int] for resizing (width, height)
          - enhance_contrast: bool
          - reduce_noise: bool
        """
        config = config or {}
        self.target_size: Tuple[int,int] = tuple(config.get("target_size", (640, 480)))
        self.apply_contrast: bool = config.get("enhance_contrast", True)
        self.apply_noise: bool = config.get("reduce_noise", True)
        if self.apply_contrast:
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def decode_and_preprocess(self, b64_string: str) -> Optional[np.ndarray]:
        """
        Decode a base64 JPEG/PNG string and apply preprocessing.

        Args:
            b64_string: base64-encoded image data
        Returns:
            Preprocessed BGR image as numpy array, or None on failure
        """
        try:
            img_data = base64.b64decode(b64_string)
            arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                return None
            return self._preprocess(frame)
        except Exception:
            return None

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        # Resize
        w, h = self.target_size
        if (frame.shape[1], frame.shape[0]) != (w, h):
            frame = cv2.resize(frame, (w, h))

        # Noise reduction
        if self.apply_noise:
            frame = cv2.bilateralFilter(frame, 9, 75, 75)
        # Contrast enhancement
        if self.apply_contrast:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = self.clahe.apply(l)
            lab = cv2.merge((l, a, b))
            frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return frame