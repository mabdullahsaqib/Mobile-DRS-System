#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored Frame Processor for JSON-driven pipeline

Responsibilities:
- Decode base64-encoded frame data from input JSON
- Preprocess frames (resize, noise reduction, contrast enhancement)
- Provide ROI extraction and (optional) re-encoding
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
        self.target_size = config.get("target_size", [640, 480])
        self.apply_contrast = config.get("enhance_contrast", True)
        self.apply_noise = config.get("reduce_noise", True)
        if self.apply_contrast:
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def decode_and_preprocess(self, b64_string: str) -> np.ndarray:
        """
        Decode a base64 JPEG/PNG string and apply preprocessing.

        Args:
            b64_string: base64-encoded image data
        Returns:
            Preprocessed BGR image as numpy array
        """
        # Decode base64 to bytes
        img_data = base64.b64decode(b64_string)
        arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image from base64 input")
        return self._preprocess(frame)

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

    def extract_roi(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract region of interest given bbox (x, y, w, h).
        """
        x, y, w, h = bbox
        y2 = min(y + h, frame.shape[0])
        x2 = min(x + w, frame.shape[1])
        return frame[y:y2, x:x2]

    def encode_to_base64(self, frame: np.ndarray, fmt: str = 'jpg', quality: int = 90) -> str:
        """
        Encode BGR image to base64 string.
        """
        if fmt.lower() == 'jpg':
            params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            ext = '.jpg'
        elif fmt.lower() == 'png':
            params = []
            ext = '.png'
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        success, buf = cv2.imencode(ext, frame, params)
        if not success:
            raise RuntimeError("Failed to encode frame to image format")
        return base64.b64encode(buf).decode('utf-8')
