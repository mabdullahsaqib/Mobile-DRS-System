from typing import List, Dict, Optional
from modules.trajectory_analysis.models.Input_model import Position3D, Velocity3D, Spin

# Constants
GRAVITY = -9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³
BALL_RADIUS = 0.036  # meters
BALL_AREA = 3.1416 * BALL_RADIUS**2  # m²
DRAG_COEFF = 0.47
TIME_STEP = 0.01  # seconds
STUMP_X = 0.0  # Position of the stumps (typically at x = 0)

def cross_product(v1, v2):
    """Compute the cross product of two 3D vectors."""
    return Velocity3D(
        x = v1.y * v2.z - v1.z * v2.y,
        y = v1.z * v2.x - v1.x * v2.z,
        z = v1.x * v2.y - v1.y * v2.x
    )

def compute_trajectory(
    current_pos: Position3D,
    velocity: Velocity3D,
    spin: Spin,
    edge_detected: bool,
    stop_x: float = STUMP_X
) -> List[Dict]:
    """
    Computes the trajectory of a spinning cricket ball starting near batter's pads
    and ending at the stump plane (x = stop_x). Models:
    - Gravity
    - Air drag
    - Magnus lift due to spin
    """
    trajectory = []
    pos = current_pos
    vel = velocity

    for step in range(1, 1001):  # Simulate up to 10 seconds
        speed = (vel.x**2 + vel.y**2 + vel.z**2) ** 0.5

        # Drag force
        drag_force = Velocity3D(0, 0, 0) # type: ignore
        if speed > 1e-6:
            drag_magnitude = 0.5 * AIR_DENSITY * DRAG_COEFF * BALL_AREA * speed**2
            drag_force = Velocity3D(
                x = -drag_magnitude * vel.x / speed,
                y = -drag_magnitude * vel.y / speed,
                z = -drag_magnitude * vel.z / speed,
            )

        # Magnus lift from spin
        lift_force = cross_product(spin.axis, vel)
        lift_force = Velocity3D(
            x = lift_force.x * spin.rate,
            y = lift_force.y * spin.rate,
            z = lift_force.z * spin.rate,
        )

        # Total acceleration
        acc = Velocity3D(
            x = drag_force.x + lift_force.x,
            y = drag_force.y + lift_force.y,
            z = drag_force.z + lift_force.z + GRAVITY,
        )

        # Euler integration
        vel = Velocity3D(
            x = vel.x + acc.x * TIME_STEP,
            y = vel.y + acc.y * TIME_STEP,
            z = vel.z + acc.z * TIME_STEP,
        )
        pos = Position3D(
            x = pos.x + vel.x * TIME_STEP,
            y = pos.y + vel.y * TIME_STEP,
            z = pos.z + vel.z * TIME_STEP,
        )

        trajectory.append({
            "time_offset": step * TIME_STEP,
            "position": {"x": pos.x, "y": pos.y, "z": pos.z},
            "velocity": {"x": vel.x, "y": vel.y, "z": vel.z},
        })

        # Stop if we pass the stump plane
        if (current_pos.x > stop_x and pos.x <= stop_x) or (current_pos.x < stop_x and pos.x >= stop_x):
            break

    return trajectory


def calculate_velocity(p1, p2, t1, t2):
    """Calculate 2D velocity vector between two points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dt = t2 - t1
    if dt == 0:
        return (0, 0)
    return (dx / dt, dy / dt)


def process_ball_data(frames):
    ball_positions = []
    timestamps = []

    for frame in frames:
        detections = frame.get("detections", {})
        ball_detections = detections.get("ball", [])

        if ball_detections:
            # Assuming we're interested in the first detected ball
            ball = ball_detections[0]
            center = ball.get("center")
            timestamp = frame.get("timestamp")

            if center and timestamp is not None:
                ball_positions.append(center)
                timestamps.append(timestamp)

    return ball_positions, timestamps


def get_stump_positions():
    return;


def detect_bounce(
    ball_positions: List[List[float]]
) -> Optional[int]:
    """
    Detects the frame index where the ball bounces.
    Simple method: Bounce typically seen when y-coordinate increases after a decrease.
    (In most camera setups, vertical coordinate 'y' grows downward.)
    """
    for i in range(1, len(ball_positions) - 1):
        prev_y = ball_positions[i - 1][1]
        curr_y = ball_positions[i][1]
        next_y = ball_positions[i + 1][1]

        if curr_y > prev_y and next_y < curr_y:
            return i
    return None
