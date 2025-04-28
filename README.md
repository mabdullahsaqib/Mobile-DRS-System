# Ball and Object Tracking Module

This module is responsible for detecting and tracking critical objects in cricket matches, including the ball, stumps, batsman, and bat. It calculates the ball's 3D coordinates (x,y,z) over time, along with stump and batsman positions.

## Project Structure

The module is organized into the following components:

- `main.py`: Main entry point and orchestration
- `frame_processor.py`: Video frame processing and preprocessing
- `object_detector.py`: Detection of cricket objects using hybrid approach
- `ball_tracker.py`: Ball tracking and trajectory calculation
- `player_tracker.py`: Batsman and bat tracking
- `stump_detector.py`: Stump detection and bail status monitoring
- `calibration.py`: Camera calibration for 3D position estimation
- `data_models.py`: Data structures for tracking information
- `utils.py`: Utility functions for logging, visualization, etc.

## Team Member Responsibilities

The implementation is divided among 5 team members:

### Member 1 (Team Lead)
- Overall architecture and integration (`main.py`)
- Data model design and validation (`data_models.py`)
- Performance optimization
- Integration testing

### Member 2
- Frame processing and image preprocessing (`frame_processor.py`)
- Camera calibration algorithms (`calibration.py`)
- Mobile optimization
- Input/output handling

### Member 3
- Object detection implementation (`object_detector.py`)
- Utility functions and visualization (`utils.py`)
- Model training/integration
- Detection optimization

### Member 4
- Ball tracking algorithms (`ball_tracker.py`)
- Player tracking algorithms (`player_tracker.py`)
- Trajectory calculation
- Physics modeling

### Member 5
- Stump detection algorithms (`stump_detector.py`)
- Pitch analysis
- Bail status monitoring
- 3D coordinate system validation

## Iterative Development Plan

The module will be developed in iterations:

### Iteration 1: Basic Framework and Detection
- Set up project structure and interfaces
- Implement basic frame processing
- Implement simple object detection for cricket ball and stumps
- Create visualization utilities

### Iteration 2: Tracking and 3D Positioning
- Implement ball tracking across frames
- Add camera calibration for 3D positioning
- Implement basic trajectory calculation
- Add batsman detection

### Iteration 3: Advanced Features
- Implement bat tracking and edge detection
- Add physics-based trajectory prediction
- Implement bail status monitoring
- Enhance detection accuracy with deep learning

### Iteration 4: Optimization and Integration
- Optimize for mobile performance
- Implement error handling and recovery
- Add comprehensive logging
- Integrate with other DRS modules

### Iteration 5: Testing and Refinement
- Comprehensive testing with various cricket scenarios
- Fine-tune detection parameters
- Optimize memory usage and battery consumption
- Final integration and documentation

## Getting Started

### Prerequisites
- Python 3.8+
- OpenCV 4.5+
- NumPy
- Matplotlib (for visualization)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Module
```bash
python src/main.py --config config.json
```

For testing with a video file:
```bash
python src/main.py --config config.json --input /path/to/video.mp4 --visualize
```

## Configuration

The module is configured via a JSON file. Example configuration:

```json
{
  "frame_processor": {
    "target_size": [640, 480],
    "enhance_contrast": true,
    "reduce_noise": true
  },
  "object_detector": {
    "detection_method": "hybrid",
    "confidence_threshold": 0.5
  },
  "ball_tracker": {
    "use_kalman": true,
    "max_tracking_distance": 100,
    "gravity": 9.8
  },
  "logging": {
    "level": "INFO",
    "file": "ball_tracking.log"
  }
}
```

## Mobile Optimization

The module is designed for mobile applications with the following optimizations:
- Efficient frame processing with optional downscaling
- Selective deep learning usage to balance accuracy and performance
- Memory-efficient data structures
- Configurable processing pipeline to adapt to device capabilities

## please use the following command to run the code
python main.py --config config.json --input batsman.mp4 --visualize

## use detection method= deep_learning for detecting person in config.json and method=traditional for ball and stumps detection
## files changed= object_detector.py, main (to visualize the detections), added yolo folder, and config.json
