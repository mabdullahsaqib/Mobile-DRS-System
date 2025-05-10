#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored main.py for JSON-driven Ball and Bat Tracking Module

Replaces video capture with input.json parsing, and outputs output.json.
No CLI argument parsing; this module exposes a `main` function that the wrapper app can call.
"""
import json
import cv2
from typing import Optional
from frame_processor import FrameProcessor
from object_detector import ObjectDetector
from stump_detector import StumpDetector
from ball_tracker import BallTracker
from batsman_tracker import BatsmanTracker

config_path = "config.json"

def main(input_json_path: str, output_json_path: str, visualize: bool = False):
    with open(config_path, 'r') as cfp:
        config = json.load(cfp)

    processor = FrameProcessor(config.get('frame_processor', {}))
    detector = ObjectDetector(config.get('object_detector', {}))
    stump_detector = StumpDetector(config.get('stump_detector', {}))
    ball_tracker = BallTracker(config.get('ball_tracker', {}))
    batsman_tracker = BatsmanTracker(focal_length=config.get('batsman_tracker', {}).get('focal_length', 1500))
    stump_detector.update_interval = config.get('stump_detector', {}).get('update_interval', 1)

    with open(input_json_path, 'r') as f:
        data = json.load(f)

    all_outputs = []
    historical_positions = []

    for entry in data.get('results', []):
        frame_id = entry.get('frameId')
        timestamp = entry.get('timestamp', None)

        # Decode and preprocess frame
        frame_b64 = entry.get('frameData')
        frame = processor.decode_frame({"data": frame_b64})

        # Detect objects
        detections = detector.detect(frame)

        # Detect stumps and merge into detections
        stumps_data = stump_detector.detect(frame, detections, frame_id)
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

        # Track ball
        trajectory_data = ball_tracker.track(frame, detections, historical_positions)
        if trajectory_data:
            historical_positions.append(trajectory_data['current_position'])

        # Track batsman
        batsman_tracker.update(detections.get('batsman', []), frame.shape, frame_id)

        # Ensure all keys exist
        for key in ['ball', 'batsman', 'bat', 'pads']:
            detections.setdefault(key, [])

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

        # Optional: preserve camera metadata
        if 'cameraPosition' in entry:
            output['camera_position'] = entry['cameraPosition']
        if 'cameraRotation' in entry:
            output['camera_rotation'] = entry['cameraRotation']

        all_outputs.append(output)
        
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

        #     cv2.imshow('Detections', frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

    # Save outputs
    with open(output_json_path, 'w') as ofp:
        json.dump(all_outputs, ofp, indent=2)

    if visualize:
        cv2.destroyAllWindows()

