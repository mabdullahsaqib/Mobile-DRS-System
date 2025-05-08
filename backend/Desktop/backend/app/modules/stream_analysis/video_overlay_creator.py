import cv2
import numpy as np
import os
from typing import Tuple, List
from tqdm import tqdm

class StreamOverlay:
    def __init__(self, config: dict):
        self.config = config
        self.validate_config()  # Ensure required configuration is provided
                # Load background image (front-view cricket pitch)
        self.bg = cv2.imread(self.config['bg_image_path'])
        if self.bg is None:
            raise FileNotFoundError(f"Background not found at {self.config['bg_image_path']}")
        # Get frame dimensions
        self.height, self.width = self.bg.shape[:2]
             
        # Create output directory if it doesn't exist
        os.makedirs(self.config['output_frame_dir'], exist_ok=True)

    def validate_config(self):
         # Ensure all required configuration keys are present
        required_keys = [
            'output_frame_dir', 'bg_image_path', 'fps',
            'ball_trajectory', 'batsman_pos', 'bat_size', 'stumps_pos',
            'decision', 'decision_frame'
        ]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing config key: {key}")

    def draw_stumps(self, frame: np.ndarray) -> np.ndarray:
             # Draw 3 stumps at specified positions
        for x, y in self.config['stumps_pos']:
            cv2.rectangle(frame, (x - 2, y), (x + 2, y + 40), (200, 180, 150), -1)
            cv2.rectangle(frame, (x - 8, y - 3), (x + 8, y), (255, 255, 255), -1)
        return frame

    def draw_batsman(self, frame: np.ndarray) -> np.ndarray:
          # Draw bat and batsman rectangle
        bat_x, bat_y = self.config['batsman_pos']
        bat_w, bat_h = self.config['bat_size']
        cv2.rectangle(frame, (bat_x, bat_y), (bat_x + bat_w, bat_y + bat_h), (50, 50, 50), -1)
        cv2.rectangle(frame, (bat_x - 10, bat_y + bat_h), (bat_x + bat_w + 10, bat_y + bat_h + 60), (0, 120, 255), -1)
        return frame

    def draw_ball(self, frame: np.ndarray, position: Tuple[int, int]) -> np.ndarray:
          # Draw red ball at given position
        cv2.circle(frame, position, 6, (0, 0, 255), -1)
        return frame

    def draw_impact_marker(self, frame: np.ndarray, frame_id: int) -> np.ndarray:
        nt) -> np.ndarray:
        # Draw impact circle and label if it's the impact frame
        if 'impact_frame' in self.config and frame_id == self.config['impact_frame']:
            if 'impact_pos' in self.config:
                pos = self.config['impact_pos']
                cv2.circle(frame, pos, 12, (0, 255, 255), 2)
                cv2.circle(frame, pos, 5, (255, 255, 0), -1)
                cv2.putText(frame, "Impact!", (pos[0] + 15, pos[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        return frame

    def draw_predicted_path(self, frame: np.ndarray, frame_id: int) -> np.ndarray:
            # Draw predicted ball trajectory after impact
        if 'predicted_path' in self.config and frame_id >= self.config.get('impact_frame', 0):
            for i in range(len(self.config['predicted_path']) - 1):
                if i % 2 == 0:
                    cv2.line(frame,
                             self.config['predicted_path'][i],
                             self.config['predicted_path'][i + 1],
                             (0, 255, 255), 2)
            if 'predicted_impact' in self.config:
                cv2.drawMarker(frame, self.config['predicted_impact'], (0, 255, 255),
                               cv2.MARKER_CROSS, 20, 2)
        return frame

    def draw_decision(self, frame: np.ndarray, frame_id: int) -> np.ndarray:
             # Display decision text (OUT/NOT OUT) from the decision frame onwards
        if frame_id >= self.config['decision_frame']:
            decision_text = f"Decision: {self.config['decision']}"
            color = (0, 255, 0) if self.config['decision'] == "NOT OUT" else (0, 0, 255)
            (w, h), _ = cv2.getTextSize(decision_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
            cv2.rectangle(frame, (10, 10), (30 + w, 30 + h), (0, 0, 0), -1)
            cv2.putText(frame, decision_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            if 'decision_info' in self.config:
                cv2.putText(frame, self.config['decision_info'], (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return frame

    def draw_ultraedge(self, frame: np.ndarray, frame_id: int) -> np.ndarray:
         # Show UltraEdge waveform for frames within a certain range
        if not self.config.get('edge_detected', False):
            return frame
        start = self.config.get('ultraedge_start_frame', 45)
        end = self.config.get('ultraedge_end_frame', 55)
        if start <= frame_id <= end:
            cv2.rectangle(frame, (self.width - 250, 50), (self.width - 50, 200), (0, 0, 0), -1)
            cv2.line(frame, (self.width - 250, 150), (self.width - 50, 150), (255, 255, 255), 1)
            for x in range(0, 200, 5):
                
                # Simulate spike in center
                height = np.random.randint(30, 50) if 90 < x < 110 else np.random.randint(5, 15)
                pt1 = (self.width - 250 + x, 150)
                pt2 = (self.width - 250 + x, 150 - height)
                cv2.line(frame, pt1, pt2, (0, 255, 255), 1)
            cv2.putText(frame, "UltraEdge", (self.width - 230, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def generate_frames(self) -> List[str]:
         # Generate each video frame with overlays
        frame_paths = []
        num_frames = len(self.config['ball_trajectory'])
        for frame_id in tqdm(range(num_frames), desc="Generating frames"):
            frame = self.bg.copy()
            frame = self.draw_stumps(frame)
            frame = self.draw_batsman(frame)
            if frame_id < len(self.config['ball_trajectory']):
                frame = self.draw_ball(frame, self.config['ball_trajectory'][frame_id])
            frame = self.draw_impact_marker(frame, frame_id)
            frame = self.draw_predicted_path(frame, frame_id)
            frame = self.draw_decision(frame, frame_id)
            frame = self.draw_ultraedge(frame, frame_id)
            frame_path = os.path.join(self.config['output_frame_dir'], f"frame_{frame_id:03d}.png")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
        print(f"✅ {num_frames} frames generated in: {self.config['output_frame_dir']}")
        return frame_paths

    def create_video(self):
            # Combine frames into a video
        frames = sorted([f for f in os.listdir(self.config['output_frame_dir']) if f.endswith(".png")])
        if not frames:
            raise Exception("No frames found.")

        fps = self.config.get('fps', 30)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.config['output_video_path'], fourcc, fps, (self.width, self.height))

        for frame_name in frames:
            frame = cv2.imread(os.path.join(self.config['output_frame_dir'], frame_name))
            out.write(frame)

        out.release()
        print(f"🎥 Video created at {self.config['output_video_path']}")


if __name__ == "__main__":
     # Sample dummy input to test the overlay functionality
    sample_config = {
        'output_frame_dir': "output/augmented_frames",
        'output_video_path': "output/overlay_video.mp4",
        'bg_image_path': "straight_view.jpg",
        'fps': 30,
        'ball_trajectory': [(360, y) for y in range(700, 200, -8)],
        'batsman_pos': (350, 180),
        'bat_size': (15, 60),
        'stumps_pos': [(340, 120), (360, 120), (380, 120)],
        'decision': "OUT",
        'decision_frame': 50,
        'decision_info': "Ball would have hit middle stump",
        'impact_frame': 35,
        'impact_pos': (360, 200),
        'predicted_path': [(360, y) for y in range(200, 120, -4)],
        'predicted_impact': (360, 120),
        'edge_detected': True,
        'ultraedge_start_frame': 45,
        'ultraedge_end_frame': 55
    }

    overlay = StreamOverlay(sample_config)
    overlay.generate_frames()
    overlay.create_video()
