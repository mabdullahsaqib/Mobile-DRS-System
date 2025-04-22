from typing import List, Dict
from modules.trajectory_analysis.models.frame_models import Position3D, Velocity3D, Spin

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
    Computes the trajectory of a spinning cricket ball starting near batter’s pads
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
        drag_force = Velocity3D(0, 0, 0)
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

# example usage

# traj = compute_trajectory(
#     current_pos=Position3D(x=1.0, y=0.0, z=0.7),  # 70cm above ground
#     velocity=Velocity3D(x=-30.0, y=0.0, z=1.0),   # toward stumps
#     spin=Spin(rate=20.0, axis=Velocity3D(x=0.0, y=0.0, z=1.0)),  # top spin
#     edge_detected=False
# )