from typing import Optional, List
from Input_model import StumpDetection
import numpy as np


class StumpTracker:
    def __init__(self, jitter_threshold: int = 5):
        self.static_positions: Optional[List[StumpDetection]] = None
        self.jitter_threshold = jitter_threshold

    def update(self, stumps: List[List[StumpDetection]]) -> List[dict]:
        if not stumps:
            return []

        valid_frames = [stumps for stumps in stumps if len(stumps) == 3]
        if not valid_frames:
            return []

        num_stumps = 3
        bbox_coords = [[] * 3]
        top_coords = [[] * 3]
        bottom_coords = [[] * 3]

        for m_stump in valid_frames:
            for i, t_stump in enumerate(m_stump):
                bbox_coords[i].append(t_stump.bbox)
                top_coords[i].append(t_stump.top)
                bottom_coords[i].append(t_stump.bottom)

        averaged_stumps = []
        for i in range(num_stumps):
            avg_bbox = np.mean(bbox_coords[i], axis=0).tolist()
            avg_top = np.mean(top_coords[i], axis=0).tolist()
            avg_bottom = np.mean(bottom_coords[i], axis=0).tolist()

            averaged_stump = StumpDetection(
                bbox=[int(coord) for coord in avg_bbox],
                confidence=1.0,
                top=[int(coord) for coord in avg_top],
                bottom=[int(coord) for coord in avg_bottom],
            )
            averaged_stumps.append(averaged_stump)

        if self.static_positions is None:
            self.static_positions = averaged_stumps
            return [s.model_dump() for s in self.static_positions]

        updated = []
        for cached, new in zip(self.static_positions, averaged_stumps):
            dx = abs(cached.bbox[0] - new.bbox[0])
            dy = abs(cached.bbox[1] - new.bbox[1])
            if dx > self.jitter_threshold or dy > self.jitter_threshold:
                cached = new
            updated.append(cached)

        if any(
            abs(c.bbox[0] - n.bbox[0]) > self.jitter_threshold
            or abs(c.bbox[1] - n.bbox[1]) > self.jitter_threshold
            for c, n in zip(self.static_positions, averaged_stumps)
        ):
            self.static_positions = updated

        return [s.model_dump() for s in self.static_positions]
