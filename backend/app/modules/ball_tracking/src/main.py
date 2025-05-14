#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py

Modular pipeline:
 - load_input: reads and parses input.json
 - preprocess_frames: uses FrameProcessor to decode images
 - detect_objects: uses ObjectDetector on frames
 - generate_output: delegates to generate_output.py to write output.json
"""
import json
from typing import List, Dict, Any, Optional, Tuple

from frame_processor import FrameProcessor
from object_detector import ObjectDetector

# Configuration path
CONFIG_PATH = "config.json"


def load_config(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def load_input(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('results', [])


def preprocess_frames(
    entries: List[Dict[str, Any]],
    processor: FrameProcessor
) -> List[Tuple[int, Optional[Any], Optional[float], Dict[str, Any]]]:
    """
    Decodes base64 frames.
    Returns list of tuples: (frame_id, frame_image or None, timestamp, metadata)
    metadata contains cameraPosition and cameraRotation if present.
    """
    processed = []
    for entry in entries:
        fid = entry.get('frameId')
        ts = entry.get('timestamp')
        frame = processor.decode_and_preprocess(entry.get('frameData', ''))
        meta = {}
        if 'cameraPosition' in entry:
            meta['camera_position'] = entry['cameraPosition']
        if 'cameraRotation' in entry:
            meta['camera_rotation'] = entry['cameraRotation']
        processed.append((fid, frame, ts, meta))
    return processed


def detect_objects(
    frames: List[Tuple[int, Any, float, Dict[str, Any]]],
    detector: ObjectDetector
) -> List[Dict[str, Any]]:
    """
    Runs detection on preprocessed frames.
    Returns list of output dicts with frame_id, timestamp, detections, and metadata.
    """
    outputs = []
    for fid, frame, ts, meta in frames:
        if frame is None:
            continue
        det = detector.detect(frame)
        record: Dict[str, Any] = {
            'frame_id': fid,
            'detections': det
        }
        record.update(meta)
        outputs.append(record)
    return outputs

def write_output(
    results: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    Serializes a list of frame-level detection records to JSON.

    - Converts any tuple bboxes or points into lists for JSON compatibility.
    - Writes pretty-printed JSON to `output_path`.
    """
    serialized = []
    for record in results:
        out_rec = {
            'frame_id': record.get('frame_id'),
            'detections': {},
        }
        # copy through camera metadata if present
        if 'camera_position' in record:
            out_rec['camera_position'] = record['camera_position']
        if 'camera_rotation' in record:
            out_rec['camera_rotation'] = record['camera_rotation']

        # process each detection category
        detections = record.get('detections', {})
        for category, items in detections.items():
            out_items = []
            for det in items:
                det_copy = det.copy()
                # convert bbox tuple to list
                bbox = det_copy.get('bbox')
                if isinstance(bbox, tuple):
                    det_copy['bbox'] = list(bbox)
                # convert any center tuple
                center = det_copy.get('center')
                if isinstance(center, tuple):
                    det_copy['center'] = list(center)
                # convert position dict z if needed (already numeric)
                out_items.append(det_copy)
            out_rec['detections'][category] = out_items

        # include optional trajectory or other keys verbatim
        if 'ball_trajectory' in record:
            out_rec['ball_trajectory'] = record['ball_trajectory']
        if 'batsman_position' in record:
            out_rec['batsman_position'] = record['batsman_position']

        serialized.append(out_rec)

    # write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)




def ball_tracking(
    input_json: str,
    output_json: str
) -> None:
    # load config and initialize
    config = load_config(CONFIG_PATH)
    processor = FrameProcessor()
    detector = ObjectDetector(config)

    # load and preprocess
    entries = load_input(input_json)
    frames = preprocess_frames(entries, processor)

    # detect objects
    results = detect_objects(frames, detector)

    # delegate output generation
    write_output(results, output_json)
