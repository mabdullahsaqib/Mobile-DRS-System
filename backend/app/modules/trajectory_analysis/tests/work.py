import json
from pathlib import Path
import sys

def extract_ball_positions(frames):
    positions = []
    for f in frames:
        bt = f.get("ball_trajectory")
        if not bt:
            continue
        cp = bt.get("current_position")
        if not cp:
            continue
        if all(k in cp for k in ("x", "y", "z")):
            positions.append((f["frame_id"], cp["x"], cp["y"], cp["z"]))
    return positions

def find_lowest_y_before(frames, end_frame_id):
    lowest = None
    lowest_frame = None
    for f in frames:
        frame_id = f.get("frame_id")
        if frame_id is None or frame_id >= end_frame_id:
            continue
        bt = f.get("ball_trajectory")
        if not bt or not bt.get("current_position"):
            continue
        y = bt["current_position"]["y"]
        if lowest is None or y < lowest:
            lowest = y
            lowest_frame = frame_id
    return lowest_frame

def find_first_z_drop(frames):
    prev_z = None
    for idx, f in enumerate(frames):
        bt = f.get("ball_trajectory")
        if not bt or not bt.get("current_position"):
            continue
        z = bt["current_position"]["z"]
        if prev_z is not None and z < prev_z:
            return frames[idx]["frame_id"] - 1
        prev_z = z
    return None

def compute_average_spin_rate(frames):
    """
    Computes the average spin rate from a list of frames.
    
    Parameters:
        frames (list): A list of frame dictionaries.
    
    Returns:
        float or None: The average spin rate, or None if no valid data found.
    """
    total_spin = 0
    count = 0
    for idx, frame in enumerate(frames):
        try:
            spin_rate = frame["ball_trajectory"]["spin"]["rate"]
            if isinstance(spin_rate, (int, float)):
                total_spin += spin_rate
                count += 1
        except (KeyError, TypeError):
            continue
    return total_spin / count if count > 0 else None



def main():
    path = Path(__file__).parent / "module2_output.json"
    if not path.exists():
        print(f"Error: file not found at {path}", file=sys.stderr)
        sys.exit(1)
    text = path.read_text()
    if not text.strip():
        print(f"Error: {path} is empty", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}", file=sys.stderr)
        sys.exit(1)
    coords = extract_ball_positions(data)
    for frame_id, x, y, z in coords:
        print(frame_id, x, y, z)
    drop_frame = find_first_z_drop(data)
    if drop_frame is not None:
        print(f"First Z drop before frame: {drop_frame}")

    bounce_frame = find_lowest_y_before(data, drop_frame)
    if bounce_frame is not None:
        print(f"Bounce point frame: {bounce_frame}")
    else:
        print("No valid frames before z-drop to compute bounce point.")
    average_spin_rate = compute_average_spin_rate(data)
    if average_spin_rate is None:
        print(f"Spin rate not available")    

if __name__ == "__main__":
    main()