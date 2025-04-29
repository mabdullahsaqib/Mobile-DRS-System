import cv2
import json
from .frame_processor import FrameProcessor
from .object_detector import ObjectDetector

def analyze_frame(frame, processor, detector):
    processed_frame = processor.preprocess_frame(frame)
    filtered_frame, mask = detector.isolate_objects(processed_frame)
    detections = detector.detect(filtered_frame)
    return detections

def analyze_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)

    processor = FrameProcessor(config={})
    detector = ObjectDetector(config={})
    results = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = analyze_frame(frame, processor, detector)

        results.append({
            "frame_id": frame_id,
            "detections": detections
        })

        frame_id += 1

        # Optional: Visualize detections
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save output to JSON
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    analyze_video("assets/v1.mp4", "output.json")
