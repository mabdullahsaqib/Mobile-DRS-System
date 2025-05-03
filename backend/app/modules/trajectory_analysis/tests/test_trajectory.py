import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
import numpy as np

@dataclass
class Frame3D:
    frame_id: int
    timestamp: float
    x: float
    y: float
    z: float

@dataclass
class Stump:
    top_x: float
    top_y: float
    bottom_x: float
    bottom_y: float
    top_z: float
    bottom_z: float

def load_module2_data(json_file: str) -> Tuple[List[Frame3D], List[List[Stump]]]:
    base = os.path.dirname(__file__)
    path = os.path.join(base, json_file)
    raw = json.load(open(path, 'r'))

    frames: List[Frame3D] = []
    stumps_all: List[List[Stump]] = []

    for obj in raw:
        fid = obj["frame_id"]
        ts  = float(obj["timestamp"])
        ball_det = obj["detections"]["ball"]
        if not ball_det:
            continue
        b = ball_det[0]
        cx, cy, cz = b["center3d"]
        frames.append(Frame3D(fid, ts, cx, cy, cz))

        smods: List[Stump] = []
        for s in obj["detections"]["stumps"]:
            tx, ty, tz = s["top3d"]
            bx, by, bz = s["bottom3d"]
            smods.append(Stump(tx, ty, bx, by, tz, bz))
        stumps_all.append(smods)

    return frames, stumps_all

def find_bounce_index(frames: List[Frame3D]) -> Optional[int]:
    ys = [f.y for f in frames]
    return int(np.argmin(ys)) if ys else None

def find_impact_index(frames: List[Frame3D], start: int = 0) -> Optional[int]:
    for i in range(start+1, len(frames)):
        if frames[i].z < frames[i-1].z:
            return i
    return None

def estimate_spin(frames: List[Frame3D], i_start: int, i_end: int) -> Tuple[np.ndarray, float]:
    vs = []
    for i in range(i_start+1, i_end+1):
        dt = frames[i].timestamp - frames[i-1].timestamp or 1e-6
        v = np.array([
            (frames[i].x - frames[i-1].x)/dt,
            (frames[i].y - frames[i-1].y)/dt,
            (frames[i].z - frames[i-1].z)/dt
        ])
        vs.append(v)
    if len(vs) < 2:
        return np.array([0.0, 0.0, 1.0]), 0.0
    axis = np.cross(vs[0], vs[-1])
    norm = np.linalg.norm(axis)
    axis = axis / (norm or 1.0)
    dot = np.dot(vs[0], vs[-1])
    ang = np.arccos(np.clip(dot / ((np.linalg.norm(vs[0]) * np.linalg.norm(vs[-1])) or 1.0), -1, 1))
    rate = ang / ((frames[i_end].timestamp - frames[i_start].timestamp) or 1e-6)
    return axis, rate

def simulate_with_spin(
    pos: np.ndarray, vel: np.ndarray,
    spin_axis: np.ndarray, spin_rate: float,
    z_stump: float,
    dt: float = 0.005
) -> List[Tuple[float, float, float, float]]:
    traj = []
    t = 0.0
    traj.append((t, pos[0], pos[1], pos[2]))

    g_vec = np.array([0.0, -9.81, 0.0])
    C_d = 0.005
    S = 1e-4
    while pos[2] > z_stump and pos[1] > -1.0:  # Corrected condition
        Fg = g_vec
        Fd = -C_d * np.linalg.norm(vel) * vel
        Fm = S * np.cross(spin_rate * spin_axis, vel)
        a = Fg + Fd + Fm

        vel += a * dt
        pos += vel * dt
        t += dt
        traj.append((t, pos[0], pos[1], pos[2]))
    return traj

def check_hit(final_pos: np.ndarray, stumps: List[Stump]) -> bool:
    xs = [s.top_x for s in stumps] + [s.bottom_x for s in stumps]
    ys = [s.top_y for s in stumps] + [s.bottom_y for s in stumps]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    x_ok = min_x <= final_pos[0] <= max_x
    y_ok = min_y <= final_pos[1] <= max_y
    return x_ok and y_ok

def process_full_trajectory(json_file: str) -> dict:
    frames, stumps_all = load_module2_data(json_file)
    if not frames:
        return {"error": "No ball data"}

    # 1) Bounce detection
    i_b = find_bounce_index(frames) or 0

    # 2) Impact detection (first z-drop)
    i_imp = find_impact_index(frames, i_b) or i_b

    # 3) Spin estimation between bounce and impact
    axis, rate = estimate_spin(frames, i_b, i_imp)

    # 4) Initial position & velocity at impact
    f0 = frames[i_imp]
    f_prev = frames[max(i_imp-1, 0)]
    dt0 = f0.timestamp - f_prev.timestamp or 1e-6
    v0 = np.array([
        (f0.x - f_prev.x) / dt0,
        (f0.y - f_prev.y) / dt0,
        (f0.z - f_prev.z) / dt0
    ])
    p0 = np.array([f0.x, f0.y, f0.z])

    # 5) Stump plane depth (mean of stump tops)
    stumps = stumps_all[i_imp]
    z_stump = float(np.mean([s.top_z for s in stumps]))  # cast to Python float

    # 6) Simulate the trajectory
    traj = simulate_with_spin(p0, v0, axis, rate, z_stump)

    # 7) Hit test on the final point
    final_t, final_x, final_y, final_z = traj[-1]
    hit = check_hit(np.array([final_x, final_y, final_z]), stumps)

    # Return a structured result
    return {
        "bounce_index": i_b,
        "impact_index": i_imp,
        "spin_axis": axis.tolist(),
        "spin_rate": rate,
        "stump_depth": z_stump,
        "hit": hit,
        "trajectory": [
            {"t": round(t, 3), "x": x, "y": y, "z": z}
            for (t, x, y, z) in traj
        ]
    }
import json
import numpy as np

def make_json_serializable(obj):
    """
    Recursively convert numpy types to native Python types.
    """
    if isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    else:
        return obj

result = process_full_trajectory("module2_output.json")
serializable = make_json_serializable(result)

with open("output.json", "w") as f:
    json.dump(serializable, f, indent=2)

if __name__ == "__main__":
    import pprint
    # result = process_full_trajectory("module2_output.json")
    import json
    result = process_full_trajectory("module2_output.json")
    pprint.pprint(result, width=120)
    make_json_serializable(result)
    