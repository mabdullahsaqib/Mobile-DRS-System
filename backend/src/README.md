# Ball and Object Tracking Module

This module is responsible for detecting and tracking critical objects in cricket matches, including the ball, stumps, batsman, and bat. It calculates the ball's 3D coordinates (x,y,z) over time, along with stump and batsman positions.

## Project Structure

The module is organized into the following components:

- `main.py`: Main entry point and orchestration
- `frame_processor.py`: Video frame processing and preprocessing
- `object_detector.py`: Detection of cricket objects including ball and stumps
- `ball_tracker.py`: Ball tracking and trajectory calculation

## Team Member Responsibilities

The implementation is divided among 5 team members:

## Each member has worked in collaboration with each other to implement frame processing, ball tracking and object detection which includes stumps for this sprint.


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

## please use the following command to run the code
python main.py --config config.json --input batsman.mp4 --visualize
