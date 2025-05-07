#!/usr/bin/env python3
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Frame3D:
    x: float; y: float; z: float; t: float

@dataclass
class Stump3D:
    x: float; y_top: float; y_bottom: float; z: float; radius: float = 0.05

# 1) Example path: z peaks at frame2 then drops at frame3 (impact at index 3)
frames = [
    Frame3D(0.0, 1.0, 5.0,  0.00),
    Frame3D(0.5, 1.1, 5.5,  0.05),
    Frame3D(1.0, 1.2, 6.0,  0.10),  # z-peak
    Frame3D(1.5, 1.3, 5.8,  0.15),  # impact frame
    Frame3D(2.0, 1.4, 5.6,  0.20),
    Frame3D(2.5, 1.5, 5.4,  0.25),
]

# one stump at x=2.0, plane z=7.0
stumps    = [Stump3D(2.0, 0.0, 0.71, 7.0)]
spin_axis = np.array([0.0, 1.0, 0.0])
spin_rate = 20.0

def find_impact_index(frames: List[Frame3D]) -> Optional[int]:
    for i in range(1, len(frames)):
        if frames[i].z < frames[i-1].z:
            return i
    return None

def simulate_trajectory(
    pos: np.ndarray,
    vel: np.ndarray,
    spin_axis: np.ndarray,
    spin_rate: float,
    stump_z: float,
    dt: float = 0.3
) -> List[Tuple[float,float,float,float]]:
    g     = np.array([0.0, -9.81, 0.0])
    omega = spin_rate * spin_axis
    t     = 0.0
    traj  = []

    while pos[2] < stump_z:
        traj.append((t, pos[0], pos[1], pos[2]))
        # simple Magnus side-force
        Fm  = 1e-3 * np.cross(omega, vel)
        a   = g + Fm
        vel = vel + a * dt
        pos = pos + vel * dt
        t  += dt

    # add the exact crossing point at stump_z
    # linear interpolate last segment
    t_prev, x_prev, y_prev, z_prev = traj[-1]
    t_last, x_last, y_last, z_last = t, pos[0], pos[1], pos[2]
    frac = (stump_z - z_prev) / (z_last - z_prev)
    # clamp
    frac = max(0.0, min(1.0, frac))
    t_cross = t_prev + frac * dt
    x_cross = x_prev + frac * (x_last - x_prev)
    y_cross = y_prev + frac * (y_last - y_prev)
    traj.append((t_cross, x_cross, y_cross, stump_z))

    return traj

def check_hit(traj: List[Tuple[float,float,float,float]], stumps: List[Stump3D]) -> bool:
    for (_, x, y, z) in traj:
        for s in stumps:
            if abs(z - s.z) < 1e-6:
                dx = x - s.x
                dy = y - ((s.y_top + s.y_bottom)/2)
                if dx*dx + dy*dy <= s.radius**2:
                    return True
    return False

def main():
    idx = find_impact_index(frames)
    if idx is None:
        print("No impact found.")
        return

    # start at impact frame
    f0 = frames[idx]
    f1 = frames[idx-1]
    dt0 = f0.t - f1.t or 1e-6
    vel0 = np.array([
        (f0.x - f1.x)/dt0,
        (f0.y - f1.y)/dt0,
        (f0.z - f1.z)/dt0
    ])
    pos0 = np.array([f0.x, f0.y, f0.z])

    print(f"Start at frame {idx}: pos={pos0}, vel={vel0}\n")

    traj = simulate_trajectory(pos0, vel0, spin_axis, spin_rate, stump_z=stumps[0].z)

    print("Trajectory points (0.3 s steps) until stump plane:")
    for t, x, y, z in traj:
        print(f"  t={t:.3f}  x={x:.3f}  y={y:.3f}  z={z:.3f}")

    print("\nHit stump?", check_hit(traj, stumps))

if __name__ == "__main__":
    main()
