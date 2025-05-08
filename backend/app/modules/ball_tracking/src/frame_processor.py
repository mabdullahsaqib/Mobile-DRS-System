#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frame Processor Module

This module is responsible for processing input video frames, including decoding,
preprocessing, and preparing frames for object detection and tracking.

Team Member Responsibilities:
----------------------------
Member 2: Frame processing, image preprocessing, and optimization for mobile devices
"""

import cv2
import numpy as np
import base64
from typing import Dict, Any, Tuple

class FrameProcessor:
    """
    Processes input frames for the Ball Tracking Module.
    
    Handles frame decoding, resizing, color conversion, and other preprocessing
    steps to prepare frames for object detection and tracking.
    
    Team Member Responsibilities:
    ----------------------------
    Member 2: Implementation and optimization of all frame processing methods
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Frame Processor with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.target_size = config.get("target_size", (640, 480))
        self.use_gpu = config.get("use_gpu", False)
        
        # Initialize preprocessing parameters
        self.apply_contrast_enhancement = config.get("enhance_contrast", True)
        self.apply_noise_reduction = config.get("reduce_noise", True)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) if self.apply_contrast_enhancement else None
    
    def decode_frame(self, frame_data: Dict[str, Any]) -> np.ndarray:
        """
        Decode frame data from input dictionary.
        
        This method handles different input formats, including:
        - Base64 encoded image data
        - Raw numpy arrays
        - Direct OpenCV frames
        
        Args:
            frame_data: Dictionary containing frame data and metadata
            
        Returns:
            Decoded frame as numpy array (BGR format)
        """
      
        # 1) Base64 branch
        if 'data' in frame_data and isinstance(frame_data['data'], str):
            # frame_data['data'] is your Base64 string
            img_bytes = base64.b64decode(frame_data['data'])
            nparr     = np.frombuffer(img_bytes, np.uint8)
            frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2) Or, if someone passed you a raw np.ndarray under 'frame'
        elif 'frame' in frame_data and isinstance(frame_data['frame'], np.ndarray):
            frame = frame_data['frame']

        # 3) Or, if they passed the array itself
        elif isinstance(frame_data, np.ndarray):
            frame = frame_data

        else:
            raise ValueError("Unsupported frame data format")

        # 4) Finally, hand it off to your preprocessing (resize, denoise, etc.)
        return self.preprocess_frame(frame)
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing steps to the frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Preprocessed frame
        """
        # Resize if needed
        if self.target_size and (frame.shape[1], frame.shape[0]) != self.target_size:
            frame = cv2.resize(frame, self.target_size)
        
        # Apply noise reduction if enabled
        if self.apply_noise_reduction:
            frame = self._reduce_noise(frame)
        
        # Apply contrast enhancement if enabled
        if self.apply_contrast_enhancement:
            frame = self._enhance_contrast(frame)
        
        return frame
    
    def _reduce_noise(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction to the frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Noise-reduced frame
        """
        # Use bilateral filter for edge-preserving noise reduction
        return cv2.bilateralFilter(frame, 9, 75, 75)
    
    def _enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance contrast in the frame to improve object visibility.
        
        Args:
            frame: Input frame
            
        Returns:
            Contrast-enhanced frame
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        
        # Merge channels and convert back to BGR
        lab = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def extract_roi(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract region of interest from frame.
        
        Args:
            frame: Input frame
            bbox: Bounding box as (x, y, width, height)
            
        Returns:
            ROI as numpy array
        """
        x, y, w, h = bbox
        y_end = min(y + h, frame.shape[0])
        x_end = min(x + w, frame.shape[1])
        roi = frame[y:y_end, x:x_end]
        return roi
       
    
    def encode_frame(self, frame: np.ndarray, format: str = "jpg", quality: int = 90) -> str:
        """
        Encode frame to base64 string.
        
        Args:
            frame: Input frame
            format: Output format ('jpg' or 'png')
            quality: Compression quality (0-100, for jpg)
            
        Returns:
            Base64 encoded string
        """
        if format.lower() == 'jpg':
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
        elif format.lower() == 'png':
            _, buffer = cv2.imencode('.png', frame)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return base64.b64encode(buffer).decode('utf-8')
