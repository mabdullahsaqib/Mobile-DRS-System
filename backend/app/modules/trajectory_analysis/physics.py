from typing import List, Dict
from datetime import timedelta
from backend.app.modules.trajectory_analysis.models.Output_model import Position3D, Velocity3D, Spin

GRAVITY = -9.81        
AIR_DENSITY = 1.225    
BALL_RADIUS = 0.036    
BALL_AREA = 3.1416 * BALL_RADIUS**2
DRAG_COEFF = 0.47      
TIME_STEP = 0.01       

def compute_trajectory(
    current_pos: Position3D,
    velocity: Velocity3D,
    spin: Spin,
    edge_detected: bool
) -> List[Dict]:
    """
    Simple Euler‐step integration of the ball’s flight:
      - gravity in z
      - quadratic drag in all axes
      - Magnus (spin) lift approximated orthogonal to velocity & spin axis
    If edge_detected is True, we could alter spin/velocity in a future version.
    """

    traj = []
    pos = current_pos
    vel = velocity

    for step in range(1, 101): 
        speed = (vel.x**2 + vel.y**2 + vel.z**2)**0.5
        drag_mag = 0.5 * AIR_DENSITY * speed**2 * DRAG_COEFF * BALL_AREA
        if speed > 1e-6:
            drag = Velocity3D(
                x = -drag_mag * vel.x / speed,
                y = -drag_mag * vel.y / speed,
                z = -drag_mag * vel.z / speed,
            )
        else:
            drag = Velocity3D(x=0, y=0, z=0)

        lift = Velocity3D(
            x = spin.rate * (spin.axis.y * vel.z - spin.axis.z * vel.y),
            y = spin.rate * (spin.axis.z * vel.x - spin.axis.x * vel.z),
            z = spin.rate * (spin.axis.x * vel.y - spin.axis.y * vel.x),
        )

        ax = drag.x + lift.x
        ay = drag.y + lift.y
        az = drag.z + lift.z + GRAVITY

        vel = Velocity3D(
            x = vel.x + ax * TIME_STEP,
            y = vel.y + ay * TIME_STEP,
            z = vel.z + az * TIME_STEP,
        )
        pos = Position3D(
            x = pos.x + vel.x * TIME_STEP,
            y = pos.y + vel.y * TIME_STEP,
            z = pos.z + vel.z * TIME_STEP,
        )

        traj.append({
            "time_offset": step * TIME_STEP,
            "position": {"x": pos.x, "y": pos.y, "z": pos.z},
            "velocity": {"x": vel.x, "y": vel.y, "z": vel.z},
        })

        if pos.z <= 0:
            break

    return traj

def check_stumps_hit(trajectory: List[Dict], stump_x: float = 0.0, stump_radius: float = 0.2) -> bool:
    """
    Returns True if any trajectory point comes within stump_radius of
    the stump plane at x = stump_x when z ≈ 0 (ground level).
    """
    for pt in trajectory:
        px = pt["position"]["x"]
        pz = pt["position"]["z"]
        if abs(px - stump_x) <= stump_radius and pz <= 0.02:
            return True
    return False
