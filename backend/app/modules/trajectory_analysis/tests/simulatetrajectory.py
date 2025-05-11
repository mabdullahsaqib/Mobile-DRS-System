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

# 1) Example path: z peaks at idx=2 then drops at idx=3
frames = [
    Frame3D(0.0, 1.0, 5.0,  0.00),
    Frame3D(0.5, 1.1, 5.5,  0.05),
    Frame3D(1.0, 1.2, 6.0,  0.10),  # ← z-peak
    Frame3D(1.5, 1.3, 5.8,  0.15),  # impact
    Frame3D(2.0, 1.4, 5.6,  0.20),
    Frame3D(2.5, 1.5, 5.4,  0.25),
]

stumps    = [Stump3D(2.0, 0.0, 0.71, 10.0)]
spin_axis = np.array([0.0, 1.0, 0.0])
spin_rate = 20.0

def find_peak_index(frames: List[Frame3D]) -> Optional[int]:
    # local max in z
    for i in range(1, len(frames)-1):
        if frames[i].z > frames[i-1].z and frames[i].z > frames[i+1].z:
            return i
    return None

def simulate_trajectory(
    pos: np.ndarray, vel: np.ndarray,
    spin_axis: np.ndarray, spin_rate: float,
    stump_z: float, dt: float = 0.3
) -> List[Tuple[float,float,float,float]]:
    g     = np.array([0.0, -9.81, 0.0])
    omega = spin_rate * spin_axis
    t     = 0.0
    traj  = []
    while pos[2] < stump_z:
        traj.append((t, pos[0], pos[1], pos[2]))
        Fm  = 1e-3 * np.cross(omega, vel)
        a   = g + Fm
        vel = vel + a * dt
        pos = pos + vel * dt
        t  += dt
    # interpolate final crossing
    t0, x0, y0, z0 = traj[-1]
    t1, x1, y1, z1 = t, pos[0], pos[1], pos[2]
    frac = (stump_z - z0) / (z1 - z0)
    frac = max(0.0, min(1.0, frac))
    traj.append((
        t0 + frac*dt,
        x0 + frac*(x1-x0),
        y0 + frac*(y1-y0),
        stump_z
    ))
    return traj

def main():
    peak = find_peak_index(frames)
    if peak is None or peak == 0:
        print("Can't find a valid z-peak.")
        return

    # velocity from one frame before peak → peak
    f_prev = frames[peak-1]
    f_pk   = frames[peak]
    dt0    = f_pk.t - f_prev.t or 1e-6
    vel0   = np.array([
        (f_pk.x - f_prev.x) / dt0,
        (f_pk.y - f_prev.y) / dt0,
        (f_pk.z - f_prev.z) / dt0
    ])
    pos0 = np.array([f_pk.x, f_pk.y, f_pk.z])

    print(f"Starting at z-peak idx={peak}: pos={pos0}, vel={vel0}\n")

    traj = simulate_trajectory(pos0, vel0, spin_axis, spin_rate, stump_z=stumps[0].z)

    print("Trajectory points (0.3s steps) until stump plane:")
    for t, x, y, z in traj:
        print(f"  t={t:.3f}  x={x:.3f}  y={y:.3f}  z={z:.3f}")

    hit = any(
        abs(z - stumps[0].z) < 1e-6 and
        (x - stumps[0].x)**2 + (y - ((stumps[0].y_top+stumps[0].y_bottom)/2))**2
        <= stumps[0].radius**2
        for (_, x,y,z) in traj
    )
    print(f"\nHit stump? {hit}")

if __name__ == "__main__":
    main()
