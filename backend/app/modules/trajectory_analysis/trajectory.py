import numpy as np

# Test data for observed trajectory (yellow line)
# Format: [x, y, z] coordinates in meters
# x = left/right movement (negative = leg side, positive = off side)
# y = distance from bowling crease (wicket at y=20)
# z = height above ground

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Test data from previous code
observed_trajectory = np.array(
    [
        [0.00, 0.0, 2.20],  # Release point
        [0.02, 2.5, 2.35],
        [0.05, 5.0, 2.25],
        [0.08, 7.5, 2.00],
        [0.10, 10.0, 1.65],
        [0.12, 12.5, 1.25],
        [0.15, 15.0, 0.80],
        [0.18, 17.5, 0.40],  # Decision point
    ]
)

predicted_trajectory = np.array(
    [
        [0.18, 17.5, 0.40],  # Matches last observed point
        [0.22, 18.0, 0.25],
        [0.25, 18.5, 0.15],
        [0.28, 19.0, 0.08],
        [0.30, 19.5, 0.03],
        [0.31, 20.0, 0.00],  # Impact with wicket
    ]
)

wicket = {
    "stumps": [
        np.array([[-0.1143, 20.0, 0.0], [-0.1143, 20.0, 0.711]]),  # Left stump
        np.array([[0.0000, 20.0, 0.0], [0.0000, 20.0, 0.711]]),  # Middle stump
        np.array([[0.1143, 20.0, 0.0], [0.1143, 20.0, 0.711]]),  # Right stump
    ],
    "bails": [
        np.array([[-0.1143, 20.0, 0.711], [-0.05715, 20.0, 0.711]]),  # Left bail
        np.array([[0.05715, 20.0, 0.711], [0.1143, 20.0, 0.711]]),  # Right bail
    ],
}

# Create figure and 3D axis
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot observed trajectory (yellow)
ax.plot(
    observed_trajectory[:, 0],
    observed_trajectory[:, 1],
    observed_trajectory[:, 2],
    color="gold",
    linewidth=4,
    label="Observed Trajectory",
)

# Plot predicted trajectory (green)
ax.plot(
    predicted_trajectory[:, 0],
    predicted_trajectory[:, 1],
    predicted_trajectory[:, 2],
    color="lime",
    linewidth=4,
    linestyle="--",
    label="Predicted Trajectory",
)

# Plot decision point (red ball)
ax.scatter(
    observed_trajectory[-1, 0],
    observed_trajectory[-1, 1],
    observed_trajectory[-1, 2],
    color="red",
    s=150,
    label="DRS Decision Point",
)

# Plot wicket (brown stumps and white bails)
for stump in wicket["stumps"]:
    ax.plot(stump[:, 0], stump[:, 1], stump[:, 2], color="#8B4513", linewidth=6)

for bail in wicket["bails"]:
    ax.plot(bail[:, 0], bail[:, 1], bail[:, 2], color="white", linewidth=4)

# Add pitch reference (optional)
ax.plot(
    [-0.5, 0.5], [0, 0], [0, 0], color="#228B22", linewidth=10, alpha=0.2
)  # Bowling crease
ax.plot(
    [-0.5, 0.5], [20, 20], [0, 0], color="#228B22", linewidth=10, alpha=0.2
)  # Batting crease

# Set labels and title
ax.set_xlabel(
    "Sideways Movement (m)\nNegative = Leg side, Positive = Off side", fontsize=10
)
ax.set_ylabel("Distance from Bowler (m)", fontsize=10)
ax.set_zlabel("Ball Height (m)", fontsize=10)
ax.set_title("DRS Ball Trajectory Analysis", fontsize=14, fontweight="bold")

# Set viewing angle
ax.view_init(elev=15, azim=-50)

# Set axis limits
ax.set_xlim(-0.4, 0.4)
ax.set_ylim(0, 22)
ax.set_zlim(0, 2.5)

# Add legend and grid
ax.legend(loc="upper right")
ax.grid(True)

# Add annotations
ax.text(0.31, 20, 0.1, "Impact Point", color="red", fontsize=10)
ax.text(0, 0, 2.3, "Release Point", color="gold", fontsize=10)

plt.tight_layout()
plt.show()
