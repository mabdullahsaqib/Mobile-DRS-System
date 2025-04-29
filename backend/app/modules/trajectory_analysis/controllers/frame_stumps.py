from typing import Optional,List
from modules.trajectory_analysis.models.Input_model import StumpDetection


class StumpTracker:
    def __init__(self, jitter_threshold: int = 5):
        self.static_positions: Optional[List[StumpDetection]] = None
        self.jitter_threshold = jitter_threshold

    def update(self, stumps: List[dict]) -> List[dict]:
        # Convert raw dicts to model objects for easy field access
        detections = [StumpDetection(**s) for s in stumps]

        if self.static_positions is None:
            # First-ever detection: cache it
            self.static_positions = detections
            return [s.model_dump() for s in self.static_positions]

        # For subsequent frames, only update if any stump has moved more than threshold
        updated = []
        for cached, new in zip(self.static_positions, detections):
            dx = abs(cached.bbox[0] - new.bbox[0])
            dy = abs(cached.bbox[1] - new.bbox[1])
            if dx > self.jitter_threshold or dy > self.jitter_threshold:
                cached = new
            updated.append(cached)

        if any(
            abs(c.bbox[0] - n.bbox[0]) > self.jitter_threshold
            or abs(c.bbox[1] - n.bbox[1]) > self.jitter_threshold
            for c, n in zip(self.static_positions, detections)
        ):
            self.static_positions = updated

        return [s.model_dump() for s in self.static_positions]
