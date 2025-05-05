#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import json
import numpy as np
from frame_processor import FrameProcessor
from object_detector import ObjectDetector
from ball_tracker import BallTracker
from stump_detector import StumpDetector

def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = json.load(f)
    if "ball_tracker" in config:
        bt = config["ball_tracker"]
        if "color_thresholds" in bt:
            c = bt.pop("color_thresholds")
            bt.update({
                "red_lower1": c["red"]["lower1"], "red_upper1": c["red"]["upper1"],
                "red_lower2": c["red"]["lower2"], "red_upper2": c["red"]["upper2"],
                "white_lower": c["white"]["lower"], "white_upper": c["white"]["upper"]
            })
    return config


def project_point(pos, shape, f=None):
    h, w = shape[:2]
    f = f or w
    cx, cy = w//2, h//2
    return int(cx + pos['x']*f/pos['z']), int(cy - pos['y']*f/pos['z'])


def main(video_path: str, config_path: str = "config.json"):
    cfg = load_config(config_path)
    fps_target = None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    fps_target = cap.get(cv2.CAP_PROP_FPS) or 30

    # init modules
    fp = FrameProcessor(cfg.get("frame_processor", {}))
    od = ObjectDetector(cfg.get("object_detector", {}))
    bt = BallTracker(cfg.get("ball_tracker", {}))
    sd = StumpDetector(cfg.get("stump_detector", {}))

    historical_positions = []
    trajectory = []

    while True:
        # skip heavy processing: read but only process every frame
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # downscale for faster tracking
        small = cv2.resize(frame, None, fx=0.6, fy=0.6)
        proc = fp.decode_frame({"frame": small})
        det = od.detect(proc)

        ball_info = bt.track(proc, det, historical_positions)
        if ball_info and ball_info.get("current_position"):
            historical_positions.append(ball_info["current_position"])
        stump_info = sd.detect(proc, det)

        disp = proc.copy()
        if ball_info and ball_info.get("current_position"):
            p = ball_info["current_position"]
            x, y = project_point(p, disp.shape)
            cv2.circle(disp, (x, y), 6, (0,0,255), -1)
            trajectory.append((x,y))
            for i in range(1,len(trajectory)):
                cv2.line(disp, trajectory[i-1], trajectory[i], (255,255,0), 1)
        if stump_info and stump_info.get("position"):
            b = stump_info["position"]["base_center"]
            xb, yb = project_point(b, disp.shape)
            cv2.rectangle(disp, (xb-30,yb),(xb+30,yb+8),(0,255,0),-1)
            for bail in stump_info.get("bails",[]):
                pb = bail["position"]
                xb2,yb2 = project_point(pb, disp.shape)
                col = (0,0,255) if bail.get("is_dislodged") else (0,255,0)
                cv2.circle(disp,(xb2,yb2),6,col,-1)

        # resize display smaller
        show = cv2.resize(disp, None, fx=0.8, fy=0.8)
        cv2.imshow("Cricket Tracking", show)
        if cv2.waitKey(int(1000/fps_target)) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    if len(sys.argv)!=2:
        print("Usage: python main.py <video>")
        sys.exit(1)
    main(sys.argv[1])
