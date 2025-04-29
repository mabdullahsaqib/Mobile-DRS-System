import base64
import json

# Function to convert image to base64
def image_to_base64(image_path): # change this according to your image path 
    with open(r"C:\Users\buzz 2\OneDrive\Desktop\drs\Mobile-DRS-System\backend\app\modules\stream_analysis\straight_view.jpg", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# Convert the image to base64
image_base64 = image_to_base64("image.jpg")  # Path to your image file

# Prepare the JSON structure
test_input = {
    "original_frames": [
        {
            "frame_id": 1542,
            "timestamp": "2025-04-30T10:00:00Z",
            "data": image_base64,
            "resolution": [640, 360],
            "camera_position": [0, 0, 0],
            "pitch_yaw_roll": [0, 0, 0]
        }
    ],
    "predicted_path": [
        {
            "time_offset": 0.0,
            "position": {"x": 12.5, "y": 1.2, "z": 0.85},
            "velocity": {"x": 1.0, "y": 0.5, "z": 0.3}
        }
    ],
    "will_hit_stumps": True,
    "isOut": True
}

# Write the updated data to a new JSON file
with open("test_input.json", "w") as json_file:
    json.dump(test_input, json_file, indent=4)

print("test_input.json has been updated with base64 image data.")
