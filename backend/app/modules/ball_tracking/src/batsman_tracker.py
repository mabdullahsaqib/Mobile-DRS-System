import numpy as np

class BatsmanTracker:
    def __init__(self, focal_length=1500, real_batsman_height=1.7, max_lost_frames=10):
        self.focal_length = focal_length
        self.real_batsman_height = real_batsman_height  # meters
        self.max_lost_frames = max_lost_frames

        self.last_bbox = None
        self.last_frame_id = -1
        self.lost_frames = 0
        self.current_position = None  # Dict with x, y, z

    def update(self, detections: list, frame_shape: tuple, frame_id: int):
        """
        Process current batsman detections.

        Args:
            detections: list of dicts with 'bbox' and 'confidence'
            frame_shape: shape of the frame (height, width)
            frame_id: current frame index
        """
        if detections:
            # Pick the best (most confident) detection
            best = max(detections, key=lambda d: d['confidence'])
            self.last_bbox = best['bbox']
            self.last_frame_id = frame_id
            self.lost_frames = 0

            self.current_position = self._estimate_3d_position(best['bbox'], frame_shape)
        else:
            self.lost_frames += 1
            if self.lost_frames > self.max_lost_frames:
                self.current_position = None

    def _estimate_3d_position(self, bbox, frame_shape):
        """
        Estimate x, y, z position using bbox center and height.

        Args:
            bbox: (x, y, w, h)
            frame_shape: (height, width)
        Returns:
            dict with x, y, z in meters
        """
        x, y, w, h = bbox
        center_x = x + w / 2
        center_y = y + h / 2

        frame_height, frame_width = frame_shape[:2]

        # Normalize to [-1, 1]
        x_norm = (center_x - frame_width / 2) / (frame_width / 2)
        y_norm = (center_y - frame_height / 2) / (frame_height / 2)

        # Estimate depth (z) using height
        z = (self.focal_length * self.real_batsman_height) / h

        # Project x, y based on image position and estimated z
        x_world = x_norm * z
        y_world = -y_norm * z  # flip y to match world convention

        return {
            "x": round(float(x_world), 3),
            "y": round(float(y_world), 3),
            "z": round(float(z), 3)
        }

    def get_position(self):
        return self.current_position
