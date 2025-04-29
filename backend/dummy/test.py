import base64
from PIL import Image
from io import BytesIO
import json
# Fix Base64 padding function
def fix_base64_padding(base64_data):
    padding = len(base64_data) % 4
    if padding != 0:
        base64_data += '=' * (4 - padding)
    return base64_data

# Load the data from the JSON file
with open("test_input.json", "r") as f:
    data = json.load(f)

# Correct the Base64 padding for all frames
for frame in data['original_frames']:
    # Fix padding
    frame['data'] = fix_base64_padding(frame['data'])

    # Check if the Base64 data is valid and can be converted into an image
    try:
        # Decode the Base64 image data
        img_data = base64.b64decode(frame['data'])
        
        # Try opening the image
        img = Image.open(BytesIO(img_data))
        img.save(f"frame_{frame['frame_id']}.png")  # Save the image as a PNG for verification
        print(f"Frame {frame['frame_id']} is a valid image and has been saved.")
        
    except Exception as e:
        print(f"Error with Frame {frame['frame_id']}: {e}")

# Now, you can send this corrected data to your FastAPI backend
import requests

response = requests.post("http://localhost:8000/stream_analysis/analyze_stream", json=data)

if response.status_code == 200:
    result = response.json()
    with open("output_video.mp4", "wb") as f:
        f.write(base64.b64decode(result['augmented_stream']))
    print("Video saved successfully!")
else:
    print(f"Error: {response.status_code} {response.text}")
