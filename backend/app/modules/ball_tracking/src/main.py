#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import json
import argparse
from frame_processor import FrameProcessor
from object_detector import ObjectDetector
from stump_detector import StumpDetector
from ball_tracker import BallTracker
from batsman_tracker import BatsmanTracker
from backend.app.modules.ball_tracking.src.Mod2output import get_output_data

def parse_arguments():
    parser = argparse.ArgumentParser(description="Ball and Object Tracker Module")
    parser.add_argument('--config', type=str, default='config.json', help='Path to config file')
    parser.add_argument('--input', type=str, default='v1.mp4', help='Input video path')
    parser.add_argument('--output', type=str, default='output.json', help='Output JSON path')
    parser.add_argument('--visualize', action='store_true', help='Visualize detections')
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Load config
    with open(args.config) as f:
        config = json.load(f)

    # Initialize processors
    processor = FrameProcessor(config.get('frame_processor', {}))
    detector = ObjectDetector(config.get('object_detector', {}))
    stump_detector = StumpDetector(config.get('stump_detector', {}))
    ball_tracker = BallTracker(config.get('ball_tracker', {}))
    batsman_tracker = BatsmanTracker(focal_length=1500) 

    stump_detector.update_interval = 1
    cap = cv2.VideoCapture(args.input)
    frame_id = 0
    all_outputs = []
    historical_positions = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        processed_frame = processor.preprocess_frame(frame)
        detections = detector.detect(processed_frame)

        # Merge stump boxes every frame
        stumps_data = stump_detector.detect(frame, detections, frame_id)
        if stumps_data:
            detections['stumps'] = [{
                'bbox': [
                    stumps_data['bbox']['x'],
                    stumps_data['bbox']['y'],
                    stumps_data['bbox']['w'],
                    stumps_data['bbox']['h']
                ],
                'confidence': stumps_data['detection_confidence']
            }]
        else:
            detections['stumps'] = []

        # Track ball and compute trajectory
        trajectory_data = ball_tracker.track(processed_frame, detections, historical_positions)
        if trajectory_data:
            historical_positions.append(trajectory_data['current_position'])
            
        batsman_tracker.update(detections["batsman"], frame.shape, frame_id)


        # Ensure missing keys are filled
        detections.setdefault("ball", [])
        detections.setdefault("batsman", [])
        detections.setdefault("bat", [])
        detections.setdefault("pads", [])

        # Build output dict
        output = {
            "frame_id": frame_id,
            "timestamp": timestamp,
            "detections": {
                "ball": detections["ball"],
                "stumps": detections["stumps"],
                "batsman": detections["batsman"],
                "bat": detections["bat"],
                "pads": detections["pads"]
            },
            "ball_trajectory": trajectory_data if trajectory_data else {},
            "batsman_position": batsman_tracker.get_position() or {}

        }
        all_outputs.append(output)

        if args.visualize:
            # Visualize detections
            for obj in detections["ball"]:
                x, y, w, h = obj["bbox"]
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(processed_frame, 'Ball', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            for obj in detections["stumps"]:
                x, y, w, h = obj["bbox"]
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(processed_frame, 'Stumps', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            for obj in detections["batsman"]:
                x, y, w, h = obj["bbox"]
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(processed_frame, 'Batsman', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            
            cv2.imshow("Detections", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frame_id += 1

    cap.release()
    cv2.destroyAllWindows()

    # Save output
    with open(args.output, 'w') as f:
        json.dump(all_outputs, f, indent=2)

if __name__ == "__main__":
    main()
