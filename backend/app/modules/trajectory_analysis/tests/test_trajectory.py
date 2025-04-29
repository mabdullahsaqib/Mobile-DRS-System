# test_trajectory_fit.py

import json, os
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


# -----------------------------------------------------------------------------
# 1) Load JSON & extract only frames with ball detections
# -----------------------------------------------------------------------------
def load_ball_frames(filename: str) -> (list, List[Frame]):
    base = os.path.dirname(__file__)
    path = os.path.join(base, filename)
    with open(path, 'r') as f:
        raw = json.load(f)

    frames: List[Frame] = []
    for idx, obj in enumerate(raw):
        for b in obj['detections']['ball']:
            # center may be 'centre' or 'center'
            c = b.get('centre') or b.get('center')
            if not c or len(c) < 2:
                continue
            x, y = c[0], c[1]
            r = b.get('radius', 0.0)
            frames.append(Frame(
                raw_index=idx,
                frame_id=obj['frame_id'],
                timestamp=obj['timestamp'],
                center=(x, y),
                radius=r
            ))
    return raw, frames


# -----------------------------------------------------------------------------
# 2) Find contact frame: max radius
# -----------------------------------------------------------------------------
def find_contact_index(frames: List[Frame]) -> int:
    radii = [f.radius for f in frames]
    return int(np.argmax(radii))  # np.argmax returns first max :contentReference[oaicite:2]{index=2}


# -----------------------------------------------------------------------------
# 3) Determine stump_x (mean top-x of stumps)
# -----------------------------------------------------------------------------
def get_stump_x(raw: list, idx: int) -> float:
    stumps = raw[idx]['detections']['stumps']
    if not stumps:
        stumps = raw[0]['detections']['stumps']
    xs = [s['top'][0] for s in stumps]
    return float(sum(xs) / len(xs))


# -----------------------------------------------------------------------------
# 4) Fit a parabola y = ax² + bx + c through (x_k, y_k)
# -----------------------------------------------------------------------------
def fit_parabola(x_vals: List[float], y_vals: List[float]) -> np.ndarray:
    # degree=2 polynomial fit via least squares :contentReference[oaicite:3]{index=3}
    coeffs = np.polyfit(x_vals, y_vals, deg=2)  # returns [a, b, c] :contentReference[oaicite:4]{index=4}
    return coeffs  # highest→lowest degree


# -----------------------------------------------------------------------------
# 5) Sample the fitted parabola at many x
# -----------------------------------------------------------------------------
def sample_trajectory(
    coeffs: np.ndarray,
    x_start: float,
    x_end: float,
    n_points: int = 50
) -> List[Tuple[float, float]]:
    xs = np.linspace(x_start, x_end, n_points)
    ys = np.polyval(coeffs, xs)  # evaluate polynomial at xs :contentReference[oaicite:5]{index=5}
    return list(zip(xs.tolist(), ys.tolist()))


# -----------------------------------------------------------------------------
# 6) Main routine: glue everything together and print results
# -----------------------------------------------------------------------------
def main():
    raw, frames = load_ball_frames('module2_output.json')
    if len(frames) < 2:
        print("Not enough ball frames to fit trajectory.")
        return

    # 2) Contact frame via max radius
    cidx = find_contact_index(frames)
    contact = frames[cidx]
    print(f"Contact at frame {contact.frame_id} (idx={cidx}), radius={contact.radius}")

    # 3) Determine stump plane X
    stump_x = get_stump_x(raw, contact.raw_index)
    print(f"Stump plane at x = {stump_x:.1f}")

    # 4) Collect (x,y) from contact until crossing stump_x
    seq = frames[cidx:]
    x_vals, y_vals = [], []
    for f in seq:
        x, y = f.center
        x_vals.append(x)
        y_vals.append(y)
        # stop when crossing
        if (x_vals[0] < stump_x and x >= stump_x) or (x_vals[0] > stump_x and x <= stump_x):
            break

    print(f"Collected {len(x_vals)} points for fit: X range [{x_vals[0]:.1f}, {x_vals[-1]:.1f}]")

    # 5) Fit parabola
    coeffs = fit_parabola(x_vals, y_vals)
    a, b, c = coeffs
    print(f"Fitted parabola: y = {a:.3e} x² + {b:.3e} x + {c:.3e}")

    # 6) Sample and print trajectory
    traj = sample_trajectory(coeffs, x_vals[0], stump_x, n_points=20)
    print("\nPredicted 2D trajectory (x, y):")
    for x, y in traj:
        print(f"  x={x:.2f}\t y={y:.2f}")


if __name__ == "__main__":
    main()
