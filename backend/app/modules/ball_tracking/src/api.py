#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI Server for Ball Tracking System

This module sets up the FastAPI server that handles:
- Receiving video frames from the camera module
- Processing frames through the tracking pipeline
- Returning tracking results
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
import base64
import json
from typing import Dict, Any
import logging

# Import your existing modules
from frame_processor import FrameProcessor
from object_detector import ObjectDetector
from ball_tracker import BallTracker
from stump_detector import StumpDetector
from data_models import TrackingResult
from utils import visualize_results, setup_logging

app = FastAPI(
    title="Cricket Ball Tracking API",
    description="API for tracking cricket ball and related objects in video frames",
    version="1.0.0"
)

# Initialize components
config = {
    "frame_processor": {
        "target_size": (1280, 720),
        "enhance_contrast": True,
        "reduce_noise": True
    },
    "object_detector": {
        "detection_method": "hybrid",
        "confidence_threshold": 0.5
    },
    "ball_tracker": {
        "frame_rate": 30,
        "use_kalman": True,
        "gravity": 9.8,
        "max_lost_frames": 10
    },
    "stump_detector": {
        "min_detection_confidence": 0.5,
        "stump_height": 0.71,
        "stump_width": 0.038,
        "stump_spacing": 0.11
    },
    "logging": {
        "level": "INFO",
        "file": "ball_tracking.log"
    }
}

# Set up logging
setup_logging(config.get("logging", {}))

# Initialize components
processor = FrameProcessor(config.get("frame_processor", {}))
detector = ObjectDetector(config.get("object_detector", {}))
ball_tracker = BallTracker(config.get("ball_tracker", {}))
stump_detector = StumpDetector(config.get("stump_detector", {}))

# Historical data storage
historical_positions = []

@app.post("/process_frame", response_model=TrackingResult)
async def process_frame(request: Request):
    """
    Process a single video frame and return tracking results.
    
    Accepts frame data in the format specified in ball_tracking_interfaces.md
    Returns tracking data in the format specified in ball_tracking_interfaces.md
    """
    try:
        # Parse incoming JSON data
        data = await request.json()
        
        # Decode the frame
        frame = processor.decode_frame(data["frame_data"])
        
        # Process the frame
        processed_frame = processor.preprocess_frame(frame)
        
        # Detect objects
        detections = detector.detect(processed_frame)
        
        # Track ball
        ball_data = ball_tracker.track(processed_frame, detections, historical_positions)
        
        # Track stumps
        stumps_data = stump_detector.detect(processed_frame, detections)
        
        # Create tracking result
        tracking_result = TrackingResult(
            tracking_data={
                "frame_id": data["frame_data"]["frame_id"],
                "timestamp": data["frame_data"]["timestamp"],
                "processing_timestamp": "2025-04-02T11:02:47.145Z",  # Should use current time
                "delivery_id": data["sequence_metadata"]["delivery_id"],
                "match_id": data["sequence_metadata"]["match_id"],
                "confidence_score": 0.95  # Overall confidence
            },
            ball_trajectory=ball_data,
            stumps_data=stumps_data
        )
        
        # Store historical data (limit to last 10 frames)
        if ball_data and "current_position" in ball_data:
            historical_positions.append({
                "frame_id": data["frame_data"]["frame_id"],
                "position": ball_data["current_position"],
                "timestamp": data["frame_data"]["timestamp"]
            })
            if len(historical_positions) > 10:
                historical_positions.pop(0)
        
        return tracking_result
        
    except Exception as e:
        logging.error(f"Error processing frame: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize_frame")
async def visualize_frame(request: Request):
    """
    Process a frame and return visualization as JPEG image.
    """
    try:
        # Parse incoming JSON data
        data = await request.json()
        
        # Decode the frame
        frame = processor.decode_frame(data["frame_data"])
        
        # Process the frame through the pipeline
        processed_frame = processor.preprocess_frame(frame)
        detections = detector.detect(processed_frame)
        ball_data = ball_tracker.track(processed_frame, detections, historical_positions)
        stumps_data = stump_detector.detect(processed_frame, detections)
        
        # Create tracking result for visualization
        tracking_result = {
            "tracking_data": {
                "frame_id": data["frame_data"]["frame_id"],
                "timestamp": data["frame_data"]["timestamp"],
                "processing_timestamp": "2025-04-02T11:02:47.145Z",
                "confidence_score": 0.95
            },
            "ball_trajectory": ball_data,
            "stumps_data": stumps_data
        }
        
        # Generate visualization
        vis_frame = visualize_results(frame, tracking_result)
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', vis_frame)
        bytes_image = buffer.tobytes()
        
        return StreamingResponse(
            content=iter([bytes_image]),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        logging.error(f"Error visualizing frame: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_ball_inline")
async def check_ball_inline(request: Request):
    """
    Check if the ball is inline with the stumps.
    Uses the existing check_ball_inline implementation.
    """
    try:
        data = await request.json()
        positions = data['ball_trajectory']['positions']
        stumps = data['stumps_data']

        # Find the first position where the ball hits the ground (y close to 0)
        impact_position = next((p for p in positions if abs(p['y']) <= 0.01), None)

        if not impact_position:
            return JSONResponse(content={'inline': False})

        x_impact = impact_position['x']
        z_impact = impact_position['z']

        stumps_x = stumps['position']['base_center']['x']
        stump_z_min = min(s['top_position']['z'] for s in stumps['individual_stumps'])
        stump_z_max = max(s['top_position']['z'] for s in stumps['individual_stumps'])

        # Check if the ball hit the ground within the x range of the stumps
        inline = (abs(x_impact - stumps_x) < 0.2) and (stump_z_min <= z_impact <= stump_z_max)

        return JSONResponse(content={'inline': inline})
        
    except Exception as e:
        logging.error(f"Error checking ball inline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)