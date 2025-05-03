#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities Module

This module provides utility functions used throughout the Ball Tracking Module,
including logging, visualization, performance measurement, and helper functions.

Team Member Responsibilities:
----------------------------
Member 3: Utility functions, logging, and visualization tools
"""

import cv2
import numpy as np
import time
import logging
import os
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging configuration.
    
    Args:
        config: Dictionary containing logging configuration
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of logging utilities
    """
    log_level = config.get("level", "INFO")
    log_file = config.get("file", "ball_tracking.log")
    log_format = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Convert string log level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = level_map.get(log_level, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def calculate_fps(processing_times: List[float]) -> float:
    """
    Calculate frames per second from processing times.
    
    Args:
        processing_times: List of processing times in seconds
        
    Returns:
        Frames per second
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of performance measurement utilities
    """
    if not processing_times:
        return 0.0
    
    avg_time = sum(processing_times) / len(processing_times)
    return 1.0 / avg_time if avg_time > 0 else 0.0

def visualize_results(frame: np.ndarray, result: Dict[str, Any]) -> np.ndarray:
    """
    Visualize tracking results on the frame.
    
    Args:
        frame: Input video frame
        result: Tracking results
        
    Returns:
        Frame with visualizations
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of visualization utilities
    """
    # Create a copy of the frame for visualization
    vis_frame = frame.copy()
    
    # Draw ball trajectory
    if "ball_trajectory" in result and result["ball_trajectory"]:
        ball_data = result["ball_trajectory"]
        
        # Draw current ball position
        if "current_position" in ball_data:
            # Project 3D position to 2D image coordinates (simplified)
            pos = ball_data["current_position"]
            x, y = _project_3d_to_2d(pos, frame.shape)
            
            # Draw ball
            cv2.circle(vis_frame, (int(x), int(y)), 10, (0, 0, 255), -1)
            
            # Draw confidence
            conf = ball_data.get("detection_confidence", 0.0)
            cv2.putText(vis_frame, f"Ball: {conf:.2f}", (int(x) + 15, int(y) - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Draw historical positions
        if "historical_positions" in ball_data:
            for i, pos_data in enumerate(ball_data["historical_positions"]):
                if "position" in pos_data:
                    pos = pos_data["position"]
                    x, y = _project_3d_to_2d(pos, frame.shape)
                    
                    # Draw smaller circles for historical positions
                    radius = max(2, 8 - i)  # Decreasing size for older positions
                    alpha = max(0.3, 1.0 - i * 0.1)  # Decreasing opacity for older positions
                    color = (0, int(255 * alpha), int(255 * alpha))
                    
                    cv2.circle(vis_frame, (int(x), int(y)), radius, color, -1)
    
    # Draw batsman
    if "batsman_data" in result and result["batsman_data"]:
        batsman_data = result["batsman_data"]
        
        # Draw batsman position
        if "position" in batsman_data:
            pos = batsman_data["position"]
            x, y = _project_3d_to_2d(pos, frame.shape)
            
            # Draw batsman
            cv2.rectangle(vis_frame, (int(x) - 30, int(y) - 80), (int(x) + 30, int(y) + 80),
                         (0, 255, 0), 2)
            
            # Draw confidence
            conf = batsman_data.get("detection_confidence", 0.0)
            cv2.putText(vis_frame, f"Batsman: {conf:.2f}", (int(x) + 35, int(y)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw leg positions
        if "leg_position" in batsman_data:
            leg_pos = batsman_data["leg_position"]
            
            # Draw feet
            for foot in ["left_foot", "right_foot"]:
                if foot in leg_pos:
                    pos = leg_pos[foot]
                    x, y = _project_3d_to_2d(pos, frame.shape)
                    cv2.circle(vis_frame, (int(x), int(y)), 8, (0, 255, 255), -1)
            
            # Draw knees
            for knee in ["left_knee", "right_knee"]:
                if knee in leg_pos:
                    pos = leg_pos[knee]
                    x, y = _project_3d_to_2d(pos, frame.shape)
                    cv2.circle(vis_frame, (int(x), int(y)), 8, (0, 255, 255), -1)
    
    # Draw bat
    if "bat_data" in result and result["bat_data"]:
        bat_data = result["bat_data"]
        
        # Draw bat position
        if "position" in bat_data:
            bat_pos = bat_data["position"]
            
            # Draw handle and tip
            if "handle" in bat_pos and "tip" in bat_pos:
                handle = bat_pos["handle"]
                tip = bat_pos["tip"]
                
                handle_x, handle_y = _project_3d_to_2d(handle, frame.shape)
                tip_x, tip_y = _project_3d_to_2d(tip, frame.shape)
                
                # Draw bat as a line
                cv2.line(vis_frame, (int(handle_x), int(handle_y)), (int(tip_x), int(tip_y)),
                        (255, 0, 0), 3)
                
                # Draw handle and tip
                cv2.circle(vis_frame, (int(handle_x), int(handle_y)), 5, (255, 0, 0), -1)
                cv2.circle(vis_frame, (int(tip_x), int(tip_y)), 5, (255, 0, 0), -1)
            
            # Draw edge
            if "edge" in bat_pos:
                edge = bat_pos["edge"]
                edge_x, edge_y = _project_3d_to_2d(edge, frame.shape)
                cv2.circle(vis_frame, (int(edge_x), int(edge_y)), 5, (255, 0, 255), -1)
            
            # Draw confidence
            conf = bat_data.get("detection_confidence", 0.0)
            if "handle" in bat_pos:
                handle = bat_pos["handle"]
                x, y = _project_3d_to_2d(handle, frame.shape)
                cv2.putText(vis_frame, f"Bat: {conf:.2f}", (int(x) + 15, int(y) - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Draw stumps
    if "stumps_data" in result and result["stumps_data"]:
        stumps_data = result["stumps_data"]
        
        # Draw stumps
        if "individual_stumps" in stumps_data:
            for stump in stumps_data["individual_stumps"]:
                if "top_position" in stump:
                    top = stump["top_position"]
                    top_x, top_y = _project_3d_to_2d(top, frame.shape)
                    
                    # Calculate base position (on the ground)
                    base_x, base_y = top_x, top_y + 100  # Simplified
                    
                    # Draw stump as a line
                    cv2.line(vis_frame, (int(top_x), int(top_y)), (int(base_x), int(base_y)),
                            (255, 255, 0), 3)
        
        # Draw bails
        if "bails" in stumps_data:
            for bail in stumps_data["bails"]:
                if "position" in bail and "is_dislodged" in bail:
                    pos = bail["position"]
                    x, y = _project_3d_to_2d(pos, frame.shape)
                    
                    # Draw bail
                    color = (0, 0, 255) if bail["is_dislodged"] else (255, 255, 0)
                    cv2.circle(vis_frame, (int(x), int(y)), 5, color, -1)
        
        # Draw confidence
        conf = stumps_data.get("detection_confidence", 0.0)
        if "position" in stumps_data and "base_center" in stumps_data["position"]:
            pos = stumps_data["position"]["base_center"]
            x, y = _project_3d_to_2d(pos, frame.shape)
            cv2.putText(vis_frame, f"Stumps: {conf:.2f}", (int(x) + 15, int(y) - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Draw bounce point
    if "pitch_data" in result and result["pitch_data"] and "bounce_point" in result["pitch_data"]:
        bounce_point = result["pitch_data"]["bounce_point"]
        if bounce_point and "position" in bounce_point:
            pos = bounce_point["position"]
            x, y = _project_3d_to_2d(pos, frame.shape)
            
            # Draw bounce point
            cv2.circle(vis_frame, (int(x), int(y)), 8, (255, 0, 255), -1)
            cv2.putText(vis_frame, "Bounce", (int(x) + 10, int(y) + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
    
    # Draw overall confidence
    if "tracking_data" in result and "confidence_score" in result["tracking_data"]:
        conf = result["tracking_data"]["confidence_score"]
        cv2.putText(vis_frame, f"Overall: {conf:.2f}", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Draw frame ID
    if "tracking_data" in result and "frame_id" in result["tracking_data"]:
        frame_id = result["tracking_data"]["frame_id"]
        cv2.putText(vis_frame, f"Frame: {frame_id}", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    return vis_frame

def _project_3d_to_2d(pos: Dict[str, float], frame_shape: Tuple[int, int, int]) -> Tuple[float, float]:
    """
    Project 3D position to 2D image coordinates.
    
    This is a simplified projection for visualization purposes.
    In a real implementation, this would use proper camera calibration.
    
    Args:
        pos: 3D position as dictionary with x, y, z keys
        frame_shape: Shape of the frame
        
    Returns:
        2D image coordinates (x, y)
    """
    height, width = frame_shape[:2]
    
    # Extract 3D coordinates
    x_3d = pos.get("x", 0.0)
    y_3d = pos.get("y", 0.0)
    z_3d = pos.get("z", 0.0)
    
    # Simple projection (this would be replaced with proper camera projection)
    # Assuming camera is looking along negative z-axis
    focal_length = width
    
    # Center of the image
    cx, cy = width / 2, height / 2
    
    # Project to image coordinates
    # This is a simplified pinhole camera model
    if z_3d != 0:
        x_2d = cx + focal_length * x_3d / -z_3d
        y_2d = cy - focal_length * y_3d / -z_3d
    else:
        x_2d, y_2d = cx, cy
    
    return x_2d, y_2d

def plot_trajectory(result: Dict[str, Any], save_path: Optional[str] = None) -> Optional[Figure]:
    """
    Plot ball trajectory in 3D.
    
    Args:
        result: Tracking results
        save_path: Path to save the plot (if None, plot is not saved)
        
    Returns:
        Matplotlib figure or None if plotting fails
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of visualization utilities
    """
    try:
        # Check if ball trajectory data exists
        if "ball_trajectory" not in result or not result["ball_trajectory"]:
            return None
        
        ball_data = result["ball_trajectory"]
        
        # Check if historical positions exist
        if "historical_positions" not in ball_data or not ball_data["historical_positions"]:
            return None
        
        # Extract positions
        positions = []
        for pos_data in ball_data["historical_positions"]:
            if "position" in pos_data:
                pos = pos_data["position"]
                positions.append((pos.get("x", 0.0), pos.get("y", 0.0), pos.get("z", 0.0)))
        
        # Add current position
        if "current_position" in ball_data:
            pos = ball_data["current_position"]
            positions.append((pos.get("x", 0.0), pos.get("y", 0.0), pos.get("z", 0.0)))
        
        # Create 3D plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract x, y, z coordinates
        x = [p[0] for p in positions]
        y = [p[1] for p in positions]
        z = [p[2] for p in positions]
        
        # Plot trajectory
        ax.plot(x, z, y, 'r-', linewidth=2)  # Note: y and z are swapped for better visualization
        
        # Plot points
        ax.scatter(x, z, y, c='blue', marker='o')
        
        # Plot current position
        if positions:
            ax.scatter([positions[-1][0]], [positions[-1][2]], [positions[-1][1]], 
                      c='red', marker='o', s=100)
        
        # Add stumps if available
        if "stumps_data" in result and result["stumps_data"] and "individual_stumps" in result["stumps_data"]:
            stumps = result["stumps_data"]["individual_stumps"]
            for stump in stumps:
                if "top_position" in stump:
                    top = stump["top_position"]
                    x_stump = top.get("x", 0.0)
                    y_stump = top.get("y", 0.0)
                    z_stump = top.get("z", 0.0)
                    
                    # Draw stump as a line from ground to top
                    ax.plot([x_stump, x_stump], [z_stump, z_stump], [0, y_stump], 'y-', linewidth=3)
        
        # Add bounce point if available
        if "pitch_data" in result and result["pitch_data"] and "bounce_point" in result["pitch_data"]:
            bounce_point = result["pitch_data"]["bounce_point"]
            if bounce_point and "position" in bounce_point:
                pos = bounce_point["position"]
                x_bounce = pos.get("x", 0.0)
                y_bounce = pos.get("y", 0.0)
                z_bounce = pos.get("z", 0.0)
                
                ax.scatter([x_bounce], [z_bounce], [y_bounce], c='purple', marker='x', s=100)
                ax.text(x_bounce, z_bounce, y_bounce, "Bounce", color='purple')
        
        # Set labels and title
        ax.set_xlabel('X (meters)')
        ax.set_zlabel('Y (meters)')  # Z-axis in plot represents Y in world
        ax.set_ylabel('Z (meters)')  # Y-axis in plot represents Z in world
        ax.set_title('Ball Trajectory')
        
        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])
        
        # Save plot if requested
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting trajectory: {e}")
        return None

def save_tracking_data(result: Dict[str, Any], output_dir: str, frame_id: int) -> str:
    """
    Save tracking data to JSON file.
    
    Args:
        result: Tracking results
        output_dir: Directory to save the data
        frame_id: Frame ID
        
    Returns:
        Path to the saved file
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of data saving utilities
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename
    filename = os.path.join(output_dir, f"tracking_data_{frame_id:06d}.json")
    
    # Save data
    try:
        with open(filename, 'w') as f:
            import json
            json.dump(result, f, indent=2)
        return filename
    except Exception as e:
        logging.error(f"Error saving tracking data: {e}")
        return ""

def measure_execution_time(func):
    """
    Decorator to measure execution time of a function.
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function
        
    Team Member Responsibilities:
    ----------------------------
    Member 3: Implementation and maintenance of performance measurement utilities
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper
