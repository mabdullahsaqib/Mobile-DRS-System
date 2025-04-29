import cv2
import json
import argparse
from frame_processor import FrameProcessor
from object_detector import ObjectDetector


def parse_arguments():
    parser = argparse.ArgumentParser(description="Ball and Object Tracker Module")
    parser.add_argument('--config', type=str, default='config.json', help='Path to config file')
    parser.add_argument('--input', type=str, default='v1.mp4', help='Input video path')
    parser.add_argument('--output', type=str, default='output.json', help='Output JSON path')
    parser.add_argument('--visualize', action='store_true', help='Visualize detections')
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Load config
    with open(args.config) as f:
        config = json.load(f)

    # Initialize processors
    processor = FrameProcessor(config.get('frame_processor', {}))
    detector = ObjectDetector(config.get('object_detector', {}))

    cap = cv2.VideoCapture(args.input)
    frame_id = 0
    all_outputs = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        processed_frame = processor.preprocess_frame(frame)
        detections = detector.detect(processed_frame)

        output = {
            "frame_id": frame_id,
            "timestamp": timestamp,
            "detections": {
                "ball": detections.get("ball", []),
                "stumps": detections.get("stumps", [])
            }
        }
        all_outputs.append(output)

        if args.visualize:
            for obj in output['detections']['ball']:
                x, y, w, h = obj['bbox']
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.putText(processed_frame, 'Ball', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            for obj in output['detections']['stumps']:
                x, y, w, h = obj['bbox']
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(processed_frame, 'Stumps', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            cv2.imshow("Detections", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frame_id += 1

    cap.release()
    cv2.destroyAllWindows()

    # Save outputs
    with open(args.output, 'w') as f:
        json.dump(all_outputs, f, indent=2)


if __name__ == "__main__":
    main()
