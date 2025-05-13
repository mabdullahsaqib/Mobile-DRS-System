import numpy as np
import mediapipe as mp
import cv2
from typing import Dict, List, Any, Tuple

class BlazePoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Try 0 for faster performance
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        # Using 17 keypoints for compatibility
        self.keypointsMapping = [
            "Nose", "Left Eye", "Right Eye", "Left Ear", "Right Ear",
            "Left Shoulder", "Right Shoulder", "Left Elbow", "Right Elbow",
            "Left Wrist", "Right Wrist", "Left Hip", "Right Hip",
            "Left Knee", "Right Knee", "Left Ankle", "Right Ankle"
        ]

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        results = []
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        pose_res = self.pose.process(rgb)
        if pose_res.pose_landmarks:
            det = {}
            for idx, lm in enumerate(pose_res.pose_landmarks.landmark):
                if idx < len(self.keypointsMapping):
                    det[self.keypointsMapping[idx]] = (
                        int(lm.x * w), int(lm.y * h)
                    )
            results.append(det)
        return results

    def draw_pose(self, frame: np.ndarray, detections: List[Dict[str, Any]]):
        for det in detections:
            for x, y in det.values():
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            conns = [
                ("Left Shoulder", "Right Shoulder"),
                ("Left Shoulder", "Left Elbow"),
                ("Right Shoulder", "Right Elbow"),
                ("Left Elbow", "Left Wrist"),
                ("Right Elbow", "Right Wrist"),
                ("Left Shoulder", "Left Hip"),
                ("Right Shoulder", "Right Hip"),
                ("Left Hip", "Right Hip"),
                ("Left Hip", "Left Knee"),
                ("Right Hip", "Right Knee"),
                ("Left Knee", "Left Ankle"),
                ("Right Knee", "Right Ankle")
            ]
            for a, b in conns:
                if a in det and b in det:
                    cv2.line(frame, det[a], det[b], (255, 0, 0), 2)
        return frame

class BatsmanTracker:
    def __init__(self, config,
                 focal_length: float = 1500,
                 real_batsman_height: float = 1.7,
                 pad_height: float = 0.5,
                 max_lost_frames: int = 10):
        self.focal_length = focal_length
        self.real_batsman_height = real_batsman_height
        self.pad_height = pad_height
        self.max_lost_frames = max_lost_frames
        self.pose_detector = BlazePoseDetector()
        self.last_bbox = None
        self.lost_frames = 0
        self.current_position = None

    def track(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        raw = self._detect_batsman(frame)
        pads = self._detect_pads(frame, raw)

        batsman_output: List[Dict[str, Any]] = []
        for det in raw:
            bbox       = det["bbox"]
            confidence = det.get("confidence", 0.0)
            position   = self._estimate_3d(bbox, frame.shape)

            # extract only the six keypoints
            kp = det["pose"]
            pose = {
                "Left Wrist":     kp.get("Left Wrist"),
                "Left Elbow":     kp.get("Left Elbow"),
                "Left Shoulder":  kp.get("Left Shoulder"),
                "Right Wrist":    kp.get("Right Wrist"),
                "Right Elbow":    kp.get("Right Elbow"),
                "Right Shoulder": kp.get("Right Shoulder"),
            }

            batsman_output.append({
                "bbox":       bbox,
                "confidence": round(confidence, 3),
                "position":   position,
                "pose":       pose
            })
            
        pads_output: List[Dict[str, Any]] = []
        for p in pads:
            bbox = p["bbox"]
            side = p.get("side", "")
            pad_position = self._estimate_3d(bbox, frame.shape, real_height=self.pad_height)
            pads_output.append({
                "bbox": bbox,
                "side": side,
                "position": pad_position
            })

        return batsman_output, pads_output

    def _detect_batsman(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        try:
            poses = self.pose_detector.detect(frame)
            if not poses:
                return []
            center = (frame.shape[1] // 2, frame.shape[0] // 2)
            best = min(poses, key=lambda d: self._distance_to_center(d, center))
            if not self._is_valid(best):
                return []
            xs, ys = zip(*best.values())
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)
            bbox = [x1, y1, x2 - x1, y2 - y1]
            return [{
                "keypoints": best,
                "pose": best,
                "bbox": bbox,
                "confidence": self._pose_confidence(best)
            }]
        except Exception as e:
            print(f"Batsman detection error: {e}")
            return []

    def _detect_pads(self,
                     frame: np.ndarray,
                     bats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pads = []
        if not bats or not bats[0].get("pose"):
            return pads
        h, w = frame.shape[:2]
        lm = bats[0]["pose"]
        pairs = [("Left Hip", "Left Knee", "Left Ankle"),
                 ("Right Hip", "Right Knee", "Right Ankle")]
        for side, (hip_k, knee_k, ank_k) in zip(['left','right'], pairs):
            if all(k in lm for k in (hip_k, knee_k, ank_k)):
                hip, knee, ank = lm[hip_k], lm[knee_k], lm[ank_k]
                kx, ky = knee; hy = hip[1]; ay = ank[1]
                pad_w = int(w * 0.06)
                x1 = max(0, kx - pad_w//2)
                y1 = ky - int((ky - hy)*0.3)
                x2 = min(w, kx + pad_w//2)
                y2 = ay + int((ay - ky)*0.1)
                pads.append({
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "confidence": 0.9,
                    "side": side
                })
        return pads

    def _estimate_3d(self,
                     bbox: List[float],
                     frame_shape: Tuple[int,int,int],
                     real_height: float = None) -> Dict[str, float]:
        H = real_height or self.real_batsman_height
        x, y, bw, bh = bbox
        cx, cy = x + bw/2, y + bh/2
        fh, fw = frame_shape[0], frame_shape[1]
        x_n = (cx - fw/2)/(fw/2)
        y_n = (cy - fh/2)/(fh/2)
        z = (self.focal_length * H)/(bh + 1e-6)
        return {"x": round(x_n*z,3), "y": round(-y_n*z,3), "z": round(z,3)}

    def _distance_to_center(self,
                             det: Dict[str, Any],
                             center: Tuple[int,int]) -> float:
        # Compute midpoint between shoulders if available, else use nose
        ls = det.get("Left Shoulder")
        rs = det.get("Right Shoulder")
        if ls and rs:
            mx = (ls[0] + rs[0]) / 2
            my = (ls[1] + rs[1]) / 2
        else:
            nose = det.get("Nose")
            if nose:
                mx, my = nose
            else:
                return float('inf')
        return ((mx - center[0])**2 + (my - center[1])**2)**0.5

    def _is_valid(self, det: Dict[str, Any]) -> bool:
        req = {"Left Shoulder","Right Shoulder","Left Hip","Right Hip"}
        return req.issubset(det.keys())

    def _pose_confidence(self, det: Dict[str, Any]) -> float:
        return sum(1 for v in det.values() if v is not None)/len(det)

    def get_position(self) -> Dict[str, float]:
        return self.current_position