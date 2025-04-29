import json
import os
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

# -----------------------------------------------------------------------------
# Data container for each frame with ball data
# -----------------------------------------------------------------------------
@dataclass
class Frame:
    raw_index: int
    frame_id: int
    timestamp: float
    center: Tuple[float, float]  # (x, y)
    radius: float                # pixel radius
    z: float = 0.0               # estimated depth

# -----------------------------------------------------------------------------
# Load JSON & extract frames with ball detections
# -----------------------------------------------------------------------------
def load_ball_frames(filename: str, focal_length: float, ball_diameter: float) -> Tuple[list, List[Frame]]:
    base = os.path.dirname(__file__)
    path = os.path.join(base, filename)
    with open(path, 'r') as f:
        raw = json.load(f)

    frames: List[Frame] = []
    for idx, obj in enumerate(raw):
        for b in obj['detections']['ball']:
            c = b.get('centre') or b.get('center')
            if not c or len(c) < 2:
                continue
            x, y = c[0], c[1]
            r = b.get('radius', 0.0)
            if r == 0:
                continue
            z = (focal_length * ball_diameter) / (2 * r)
            frames.append(Frame(
                raw_index=idx,
                frame_id=obj['frame_id'],
                timestamp=obj['timestamp'],
                center=(x, y),
                radius=r,
                z=z
            ))
    return raw, frames

# -----------------------------------------------------------------------------
# Find contact frame: max radius
# -----------------------------------------------------------------------------
def find_contact_index(frames: List[Frame]) -> int:
    radii = [f.radius for f in frames]
    return int(np.argmax(radii))

# -----------------------------------------------------------------------------
# Determine stump_x (mean top-x of stumps)
# -----------------------------------------------------------------------------
def get_stump_x(raw: list, idx: int) -> float:
    stumps = raw[idx]['detections']['stumps']
    if not stumps:
        stumps = raw[0]['detections']['stumps']
    xs = [s['top'][0] for s in stumps]
    return float(sum(xs) / len(xs))

# -----------------------------------------------------------------------------
# Fit a parabola y = ax² + bx + c through (x_k, y_k)
# -----------------------------------------------------------------------------
def fit_parabola(x_vals: List[float], y_vals: List[float]) -> np.ndarray:
    coeffs = np.polyfit(x_vals, y_vals, deg=2)
    return coeffs

# -----------------------------------------------------------------------------
# Sample the fitted parabola at many x
# -----------------------------------------------------------------------------
def sample_trajectory(
    coeffs: np.ndarray,
    x_start: float,
    x_end: float,
    n_points: int = 50
) -> List[Tuple[float, float]]:
    xs = np.linspace(x_start, x_end, n_points)
    ys = np.polyval(coeffs, xs)
    return list(zip(xs.tolist(), ys.tolist()))

# -----------------------------------------------------------------------------
# Main routine: glue everything together and print results
# -----------------------------------------------------------------------------
def main():
    # Define camera parameters
    focal_length = 800.0  # in pixels
    ball_diameter = 0.22  # in meters (standard cricket ball diameter)

    raw, frames = load_ball_frames('module2_output.json', focal_length, ball_diameter)
    if len(frames) < 2:
        print("Not enough ball frames to fit trajectory.")
        return

    cidx = find_contact_index(frames)
    contact = frames[cidx]
    print(f"Contact at frame {contact.frame_id} (idx={cidx}), radius={contact.radius}")

    stump_x = get_stump_x(raw, contact.raw_index)
    print(f"Stump plane at x = {stump_x:.1f}")

    seq = frames[cidx:]
    x_vals, y_vals = [], []
    for f in seq:
        x, y = f.center
        x_vals.append(x)
        y_vals.append(y)
        if (x_vals[0] < stump_x and x >= stump_x) or (x_vals[0] > stump_x and x <= stump_x):
            break

    print(f"Collected {len(x_vals)} points for fit: X range [{x_vals[0]:.1f}, {x_vals[-1]:.1f}]")

    coeffs = fit_parabola(x_vals, y_vals)
    a, b, c = coeffs
    print(f"Fitted parabola: y = {a:.3e} x² + {b:.3e} x + {c:.3e}")

    traj = sample_trajectory(coeffs, x_vals[0], stump_x, n_points=20)
    print("\nPredicted 3D trajectory (x, y, z):")
    for i, (x, y) in enumerate(traj):
        if i < len(seq):
            z = seq[i].z
        else:
            z = seq[-1].z
        print(f"  x={x:.2f}\t y={y:.2f}\t z={z:.2f}")

if __name__ == "__main__":
    main()
