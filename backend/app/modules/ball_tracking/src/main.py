#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored main.py for JSON-driven Ball and Bat Tracking Module

Replaces video capture with input.json parsing, and outputs output.json.
No CLI argument parsing; this module exposes a `ball_tracking` function that the wrapper app can call.
"""
import json
import cv2
from typing import Optional
from modules.ball_tracking.src.frame_processor import FrameProcessor
from modules.ball_tracking.src.object_detector import ObjectDetector
from modules.ball_tracking.src.stump_detector import StumpDetector
from modules.ball_tracking.src.ball_tracker import BallTracker
from modules.ball_tracking.src.batsman_tracker import BatsmanTracker
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)


class pose_detector:
    def __init__(self):
        # Keypoint names in order
        self.keypointsMapping = [
            "Nose", "Left Eye", "Right Eye", "Left Ear", "Right Ear",
            "Left Shoulder", "Right Shoulder", "Left Elbow", "Right Elbow",
            "Left Wrist", "Right Wrist", "Left Hip", "Right Hip",
            "Left Knee", "Right Knee", "Left Ankle", "Right Ankle"
        ]
        
        # Skeleton connections by index
        self.POSE_PAIRS = [
            (5, 6),   # Left Shoulder - Right Shoulder
            (5, 7), (7, 9),  # Left Arm
            (6, 8), (8, 10), # Right Arm
            (5, 11), (6, 12), # Torso sides
            (11, 12),        # Hips
            (11, 13), (13, 15), # Left Leg
            (12, 14), (14, 16)  # Right Leg
        ]
        
        # Yellow color for all keypoints
        self.colors = [(0, 255, 255)] * len(self.keypointsMapping)  # BGR: Yellow

config_path = "modules/ball_tracking/src/config.json"

def ball_tracking(input_json_path: str, output_json_path: str, visualize: bool = False):
    # Initialize call tracking variable
    call_check = ""
    
    # Load configuration
    with open(config_path, 'r') as cfp:
        config = json.load(cfp)
    call_check = "config_loaded"

    # Initialize modules with config
    processor = FrameProcessor(config.get('frame_processor', {}))
    call_check = "processor_initialized"
    
    detector = ObjectDetector(config.get('object_detector', {}))
    call_check = "detector_initialized"
    
    stump_detector = StumpDetector(config.get('stump_detector', {}))
    call_check = "stump_detector_initialized"
    
    ball_tracker = BallTracker(config.get('ball_tracker', {}))
    call_check = "ball_tracker_initialized"
    
    batsman_tracker = BatsmanTracker(focal_length=config.get('batsman_tracker', {}).get('focal_length', 1500))
    call_check = "batsman_tracker_initialized"
    
    stump_detector.update_interval = config.get('stump_detector', {}).get('update_interval', 1)
    call_check = "modules_initialized"

    # Read input JSON
    with open(input_json_path, 'r') as f:
        data = json.load(f)
    call_check = "input_json_loaded"

    try:

        all_outputs = []
        historical_positions = []

        # Process each frame entry
        for entry in data.get('results', []):
            frame_id = entry.get('frameId')
            timestamp = entry.get('timestamp', None)
            call_check = f"processing_frame_{frame_id}"
            
            # Decode and preprocess frame
            frame_b64 = entry.get('frameData')
            
            if not frame_b64:
                print(f"Frame data missing for frame ID {frame_id}. Skipping.")
                continue

            frame = processor.decode_and_preprocess(frame_b64)
            call_check = f"frame_{frame_id}_decoded"

            if frame is None:
                print(f"Failed to decode frame data for frame ID {frame_id}. Skipping.")
                continue
                
            # Detect objects
            detections = detector.detect(frame)
            call_check = f"objects_detected_frame_{frame_id}"

            if not detections:
                print(f"No detections found for frame ID {frame_id}. Skipping.")
                continue
            
            # Detect stumps and merge into detections
            stumps_data = stump_detector.detect(frame, detections, frame_id)
            call_check = f"stumps_detected_frame_{frame_id}"
            
            if stumps_data:
                detections['stumps'] = [{
                    'bbox': [
                        stumps_data['bbox']['x'],
                        stumps_data['bbox']['y'],
                        stumps_data['bbox']['w'],
                        stumps_data['bbox']['h'],
                    ],
                    'confidence': stumps_data['detection_confidence']
                }]
            else:
                detections['stumps'] = []
            call_check = f"stumps_processed_frame_{frame_id}"

            # Track ball
            trajectory_data = ball_tracker.track(frame, detections, historical_positions)
            call_check = f"ball_tracked_frame_{frame_id}"
            
            if trajectory_data:
                historical_positions.append(trajectory_data['current_position'])
            call_check = f"trajectory_processed_frame_{frame_id}"

            # Track batsman
            batsman_tracker.update(detections.get('batsman', []), frame.shape, frame_id)
            call_check = f"batsman_tracked_frame_{frame_id}"

            # Ensure all keys exist
            for key in ['ball', 'batsman', 'bat', 'pads']:
                detections.setdefault(key, [])
            call_check = f"detections_normalized_frame_{frame_id}"

            # Build output record
            output = {
                'frame_id': frame_id,
                'timestamp': timestamp,
                'detections': {
                    'ball': detections['ball'],
                    'stumps': detections['stumps'],
                    'batsman': detections['batsman'],
                    'bat': detections['bat'],
                    'pads': detections['pads'],
                },
                'ball_trajectory': trajectory_data or {},
                'batsman_position': batsman_tracker.get_position() or {}
            }
            call_check = f"output_built_frame_{frame_id}"

            # Optional: preserve camera metadata
            if 'cameraPosition' in entry:
                output['camera_position'] = entry['cameraPosition']
            if 'cameraRotation' in entry:
                output['camera_rotation'] = entry['cameraRotation']

            all_outputs.append(output)
            call_check = f"frame_{frame_id}_processed"
            
            # if visualize:
            #     for obj in detections['ball']:
            #         x, y, w, h = obj['bbox']
            #         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            #         cv2.putText(frame, 'Ball', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            #     for obj in detections['stumps']:
            #         x, y, w, h = obj['bbox']
            #         cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #         cv2.putText(frame, 'Stumps', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            #     for obj in detections['batsman']:
            #         x, y, w, h = obj['bbox']
            #         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            #         cv2.putText(frame, 'Batsman', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    except Exception as e:
        print(f"Error processing frame {frame_id}: {e} at {call_check}")
        
    # Save outputs
    with open(output_json_path, 'w') as ofp:
        json.dump(all_outputs, ofp, indent=2)
    call_check = "output_json_saved"

    return all_outputs
