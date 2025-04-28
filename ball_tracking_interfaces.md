# Ball and Object Tracking Module Interface Specification

## Overview

The Ball and Object Tracking Module is a critical component of the DRS (Decision Review System) that detects and tracks key objects in cricket matches, including the ball, stumps, batsman, and bat. This module receives video frames from the Mobile UI (Camera Module) and processes them to extract positional data, which is then passed to the Bat's Edge Detection Module.

This document defines the input and output interfaces for the Ball and Object Tracking Module to ensure seamless integration with adjacent modules.

## Input Interface

### From Mobile UI (Camera Module)

The Ball and Object Tracking Module receives video frames captured by the mobile application's camera interface. Below is the specification for the input data format:

#### Input Data Structure (JSON)

```json
{
  "frame_data": {
    "frame_id": 1542,
    "timestamp": "2025-04-02T11:02:47.123Z",
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "format": "RGB",
    "encoding": "base64",
    "data": "iVBORw0KGgoAAAANSUhEUgAA....[truncated]"
  },
  "camera_metadata": {
    "device_id": "SM-G998U-12345",
    "camera_position": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0,
      "pitch": 0.0,
      "yaw": 0.0,
      "roll": 0.0
    },
    "lens_parameters": {
      "focal_length": 4.2,
      "aperture": 1.8,
      "field_of_view": 78.0
    },
    "calibration_status": "calibrated"
  },
  "environmental_data": {
    "lighting_condition": "daylight",
    "weather": "clear",
    "wind_speed": 5.2
  },
  "sequence_metadata": {
    "delivery_id": "2025040201-D127",
    "match_id": "IPL2025-M042",
    "sequence_start_time": "2025-04-02T11:02:40.000Z",
    "is_review_request": true
  }
}
```

#### Input Fields Description

1. **frame_data**: Contains the actual video frame information
   - `frame_id`: Unique identifier for the frame in the sequence
   - `timestamp`: ISO 8601 timestamp when the frame was captured
   - `resolution`: Width and height of the frame in pixels
   - `format`: Color format of the image (RGB, YUV, etc.)
   - `encoding`: Encoding method for the image data (base64, etc.)
   - `data`: The actual image data encoded as specified

2. **camera_metadata**: Information about the capturing device
   - `device_id`: Unique identifier for the mobile device
   - `camera_position`: 3D position and orientation of the camera
     - `x`, `y`, `z`: Position coordinates in meters relative to a predefined origin (usually the center of the pitch)
     - `pitch`, `yaw`, `roll`: Camera orientation in degrees
   - `lens_parameters`: Technical specifications of the camera lens
   - `calibration_status`: Indicates if the camera has been calibrated for accurate spatial measurements

3. **environmental_data**: Contextual information about the environment
   - `lighting_condition`: Current lighting conditions that may affect image processing
   - `weather`: Weather conditions that may affect visibility
   - `wind_speed`: Wind speed in m/s that may affect ball trajectory

4. **sequence_metadata**: Information about the cricket match and delivery sequence
   - `delivery_id`: Unique identifier for the specific ball delivery
   - `match_id`: Identifier for the cricket match
   - `sequence_start_time`: When the delivery sequence started
   - `is_review_request`: Boolean indicating if this is part of a formal review request

#### Input Data Format Alternatives

The interface can also support XML format if preferred:


#### Input Stream Considerations

- The module should be able to process a continuous stream of frames at a minimum of 30 frames per second.
- Each frame should be processed independently but with awareness of previous frames for tracking continuity.
- The module should handle varying lighting conditions and camera movements.
- Calibration data may be updated periodically during a match.

## Output Interface

### To Bat's Edge Detection Module

The Ball and Object Tracking Module outputs detailed tracking data for all critical objects in the frame. This data is sent to the Bat's Edge Detection Module for further analysis. Below is the specification for the output data format:

#### Output Data Structure (JSON)

```json
{
  "tracking_data": {
    "frame_id": 1542,
    "timestamp": "2025-04-02T11:02:47.123Z",
    "processing_timestamp": "2025-04-02T11:02:47.145Z",
    "delivery_id": "2025040201-D127",
    "match_id": "IPL2025-M042",
    "confidence_score": 0.94
  },
  "ball_trajectory": {
    "current_position": {
      "x": 12.45,
      "y": 1.2,
      "z": 0.85
    },
    "velocity": {
      "x": -28.5,
      "y": 0.2,
      "z": -1.8
    },
    "acceleration": {
      "x": 0.1,
      "y": -9.8,
      "z": 0.05
    },
    "spin": {
      "axis": {
        "x": 0.1,
        "y": 0.8,
        "z": 0.2
      },
      "rate": 25.5
    },
    "detection_confidence": 0.96,
    "historical_positions": [
      {
        "frame_id": 1540,
        "position": {"x": 13.2, "y": 1.25, "z": 0.9},
        "timestamp": "2025-04-02T11:02:47.056Z"
      },
      {
        "frame_id": 1541,
        "position": {"x": 12.8, "y": 1.22, "z": 0.87},
        "timestamp": "2025-04-02T11:02:47.089Z"
      }
    ]
  },
  "batsman_data": {
    "position": {
      "x": 10.2,
      "y": 0.0,
      "z": 0.0
    },
    "leg_position": {
      "left_foot": {
        "x": 10.1,
        "y": 0.0,
        "z": -0.2
      },
      "right_foot": {
        "x": 10.3,
        "y": 0.0,
        "z": 0.2
      },
      "left_knee": {
        "x": 10.1,
        "y": 0.5,
        "z": -0.15
      },
      "right_knee": {
        "x": 10.3,
        "y": 0.5,
        "z": 0.15
      }
    },
    "stance": "right-handed",
    "body_orientation": {
      "pitch": 5.0,
      "yaw": 85.0,
      "roll": 2.0
    },
    "detection_confidence": 0.92
  },
  "bat_data": {
    "position": {
      "handle": {
        "x": 10.4,
        "y": 1.1,
        "z": 0.1
      },
      "middle": {
        "x": 10.6,
        "y": 0.7,
        "z": 0.2
      },
      "edge": {
        "x": 10.65,
        "y": 0.7,
        "z": 0.22
      },
      "tip": {
        "x": 10.8,
        "y": 0.3,
        "z": 0.3
      }
    },
    "orientation": {
      "pitch": 45.0,
      "yaw": 10.0,
      "roll": 5.0
    },
    "velocity": {
      "x": 5.2,
      "y": -2.1,
      "z": 0.5
    },
    "detection_confidence": 0.91
  },
  "stumps_data": {
    "position": {
      "base_center": {
        "x": 9.0,
        "y": 0.0,
        "z": 0.0
      }
    },
    "orientation": {
      "pitch": 0.0,
      "yaw": 0.0,
      "roll": 0.0
    },
    "individual_stumps": [
      {
        "id": "leg",
        "top_position": {"x": 9.0, "y": 0.71, "z": -0.11}
      },
      {
        "id": "middle",
        "top_position": {"x": 9.0, "y": 0.71, "z": 0.0}
      },
      {
        "id": "off",
        "top_position": {"x": 9.0, "y": 0.71, "z": 0.11}
      }
    ],
    "bails": [
      {
        "id": "leg_bail",
        "position": {"x": 9.0, "y": 0.71, "z": -0.055},
        "is_dislodged": false
      },
      {
        "id": "off_bail",
        "position": {"x": 9.0, "y": 0.71, "z": 0.055},
        "is_dislodged": false
      }
    ],
    "detection_confidence": 0.98
  },
  "pitch_data": {
    "pitch_map": {
      "length": 20.12,
      "width": 3.05,
      "center": {"x": 0.0, "y": 0.0, "z": 0.0}
    },
    "bounce_point": {
      "position": {"x": 11.2, "y": 0.0, "z": 0.1},
      "frame_id": 1538,
      "timestamp": "2025-04-02T11:02:46.989Z",
      "detection_confidence": 0.89
    }
  }
}
```

#### Output Fields Description

1. **tracking_data**: General metadata about the tracking information
   - `frame_id`: Identifier matching the input frame
   - `timestamp`: Original timestamp from the input frame
   - `processing_timestamp`: When the tracking data was generated
   - `delivery_id` and `match_id`: Identifiers from the input metadata
   - `confidence_score`: Overall confidence in the tracking data (0.0-1.0)

2. **ball_trajectory**: Detailed information about the ball's position and movement
   - `current_position`: 3D coordinates (x,y,z) in meters from the pitch center
   - `velocity`: Speed vector in m/s
   - `acceleration`: Acceleration vector in m/s²
   - `spin`: Ball rotation data including axis and rate (revolutions per minute)
   - `detection_confidence`: Confidence level for ball detection (0.0-1.0)
   - `historical_positions`: Array of previous positions for trajectory analysis

3. **batsman_data**: Information about the batsman's position and stance
   - `position`: Center position of the batsman
   - `leg_position`: Detailed positions of feet and knees for LBW analysis
   - `stance`: Batting style (right-handed or left-handed)
   - `body_orientation`: Body angle in degrees
   - `detection_confidence`: Confidence level for batsman detection (0.0-1.0)

4. **bat_data**: Information about the bat's position and movement
   - `position`: 3D coordinates for different parts of the bat
   - `orientation`: Bat angle in degrees
   - `velocity`: Bat movement speed and direction
   - `detection_confidence`: Confidence level for bat detection (0.0-1.0)

5. **stumps_data**: Information about the wicket
   - `position`: Base center position of the stumps
   - `orientation`: Stumps angle in degrees
   - `individual_stumps`: Positions of each stump
   - `bails`: Position and status of the bails
   - `detection_confidence`: Confidence level for stumps detection (0.0-1.0)

6. **pitch_data**: Information about the cricket pitch
   - `pitch_map`: Dimensions and center position of the pitch
   - `bounce_point`: Where the ball bounced on the pitch

#### Output Data Format Alternatives


#### Output Stream Considerations

- The module should output tracking data for each processed frame or at a minimum rate of 30 updates per second.
- All coordinates use a consistent coordinate system with the origin (0,0,0) at the center of the pitch at ground level.
- The x-axis runs along the length of the pitch from bowler to batsman.
- The y-axis represents height from the ground.
- The z-axis runs perpendicular to the pitch length, with positive values toward the off side for a right-handed batsman.
- Confidence scores should be provided for each detected object to indicate reliability.
- Historical positions should be included to enable trajectory analysis and prediction.

## Coordinate System Reference

To ensure consistency across all modules, the following coordinate system is used:

```
                   z+
                   ^
                   |
                   |
                   |
                   +-------> x+  (toward batsman)
                  /
                 /
                /
               v
              y+  (height)
```

- **Origin (0,0,0)**: Center of the pitch at ground level
- **X-Axis**: Along the length of the pitch, positive direction toward the batsman
- **Y-Axis**: Vertical height from the ground, positive direction upward
- **Z-Axis**: Across the width of the pitch, positive direction toward the off-side for a right-handed batsman

## Error Handling and Edge Cases

### Input Validation

The Ball and Object Tracking Module should validate incoming data and handle the following scenarios:

1. **Missing Frames**: If frames are dropped or delayed, the module should:
   - Log the missing frame IDs
   - Interpolate object positions based on previous tracking data
   - Flag the interpolated data with reduced confidence scores

2. **Poor Quality Frames**: For frames with poor visibility, motion blur, or other quality issues:
   - Process the frame with available algorithms
   - Assign appropriate (lower) confidence scores to detected objects
   - Rely more heavily on trajectory prediction from previous frames

3. **Camera Calibration Issues**: If camera calibration data is missing or invalid:
   - Use default calibration parameters
   - Flag the output data as potentially less accurate
   - Request recalibration if confidence drops below a threshold

### Output Error Handling

The module should handle the following output scenarios:

1. **Object Detection Failures**: If critical objects cannot be detected:
   - For ball: Provide estimated position based on trajectory prediction with low confidence score
   - For batsman/bat/stumps: Use last known positions with decreasing confidence scores over time
   - Include error codes in the output to indicate specific detection failures

2. **Processing Delays**: If real-time processing cannot keep up with frame rate:
   - Prioritize ball tracking over other objects
   - Consider frame skipping strategies while maintaining critical frames (e.g., ball release, bounce, bat contact)
   - Include processing delay metrics in the output

## Performance Requirements

The Ball and Object Tracking Module should meet the following performance criteria:

1. **Processing Speed**: Process frames at a minimum of 30 fps on recommended hardware
2. **Latency**: Maximum end-to-end latency of 100ms from frame capture to output generation
3. **Accuracy**:
   - Ball position accuracy: ±2cm in all dimensions
   - Object detection reliability: >95% under normal conditions
   - False positive rate: <1%
4. **Robustness**: Maintain tracking through partial occlusions and varying lighting conditions

## Implementation Recommendations

While implementation details are left to the development team, the following recommendations may help ensure optimal performance:

1. **Algorithms**:
   - Consider using a combination of traditional computer vision and deep learning approaches
   - Implement Kalman filtering for trajectory prediction and smoothing
   - Use specialized object detectors trained on cricket-specific datasets

2. **Optimization**:
   - Implement multi-threading to parallelize object detection and tracking
   - Consider GPU acceleration for neural network inference
   - Use region of interest (ROI) tracking to reduce computational load

3. **Testing**:
   - Develop a comprehensive test suite with various cricket scenarios
   - Include edge cases like unusual bowling actions, diving fielders, and extreme weather conditions
   - Validate against ground truth data from multiple camera angles

## Version Control

This interface specification is version 1.0.0. Any changes to the interface should follow semantic versioning principles:

- Major version changes (e.g., 1.0.0 → 2.0.0): Breaking changes to the interface
- Minor version changes (e.g., 1.0.0 → 1.1.0): Backward-compatible additions
- Patch version changes (e.g., 1.0.0 → 1.0.1): Bug fixes and clarifications

## Conclusion

This document provides a comprehensive specification for the Ball and Object Tracking Module interfaces within the DRS System. By adhering to these interface definitions, development teams can work independently on their respective modules while ensuring seamless integration. The JSON and XML examples provided serve as reference implementations that can be adapted based on specific project requirements.
