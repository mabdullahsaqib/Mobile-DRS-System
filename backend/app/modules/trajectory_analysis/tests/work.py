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

def compute_average_spin_and_axis_between(frames, start_frame_id, end_frame_id):
    """
    Computes the average spin rate and average spin axis (x, y, z)
    between two frame IDs (inclusive start, exclusive end).

    Parameters:
        frames (list): List of frame dictionaries.
        start_frame_id (int): The starting frame ID.
        end_frame_id (int): The ending frame ID (not inclusive).

    Returns:
        dict or None: A dictionary with average 'rate', 'axis_x', 'axis_y', 'axis_z',
                      or None if no valid data found.
    """
    total_rate = 0
    total_axis_x = 0
    total_axis_y = 0
    total_axis_z = 0
    count = 0

    for f in frames:
        frame_id = f.get("frame_id")
        if frame_id is None or not (start_frame_id <= frame_id < end_frame_id):
            continue
        try:
            spin = f["ball_trajectory"]["spin"]
            rate = spin["rate"]
            axis = spin["axis"]
            if not all(isinstance(val, (int, float)) for val in [rate, axis["x"], axis["y"], axis["z"]]):
                continue
            total_rate += rate
            total_axis_x += axis["x"]
            total_axis_y += axis["y"]
            total_axis_z += axis["z"]
            count += 1
        except (KeyError, TypeError):
            continue

    if count == 0:
        return None

    return {
        "rate": total_rate / count,
        "axis_x": total_axis_x / count,
        "axis_y": total_axis_y / count,
        "axis_z": total_axis_z / count,
    }





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
        
    if bounce_frame is not None and drop_frame is not None:
        spin_stats = compute_average_spin_and_axis_between(data, bounce_frame, drop_frame)
        if spin_stats:
            print(f"Average spin rate between bounce and z-drop: {spin_stats['rate']:.2f} rpm")
            print(f"Average spin axis: x = {spin_stats['axis_x']:.4f}, y = {spin_stats['axis_y']:.4f}, z = {spin_stats['axis_z']:.4f}")
        else:
            print(f"No valid spin data between frames {bounce_frame} and {drop_frame}.")
    

if __name__ == "__main__":
    main()