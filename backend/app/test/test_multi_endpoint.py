import requests
import base64
import json
import time

# Base URL of your local FastAPI server
BASE_URL = "http://localhost:8000"

# Simulate dummy base64 JPEG and PCM data
def get_dummy_base64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()

# Prepare a single fake frame
# fake_frame = {
#     "frameId": 0,
#     "frameData": get_dummy_base64("FAKE_JPEG_BYTES"),
#     "audioData": get_dummy_base64("FAKE_AUDIO_DATA"),
#     "cameraPosition": {"x": 0.0, "y": 0.0, "z": 0.0},
#     "cameraRotation": {"x": 0.0, "y": 0.0, "z": 0.0}
# }

# payload = {
#     "results": [fake_frame] * 5  # Send 5 dummy frames
# }

# Frame data

with open("../reviews/0b425b5d-4203-4f3a-ae56-52d5e51130f0/input.json", "r") as f:
    payload = f.read()


print("Payload loaded from file:", payload[:100], "...")  # Print first 100 chars for brevity

# decode the JSON string to a Python dictionary
payload = json.loads(payload)

# Step 1: Submit review
print("[POST] Submitting review...")
response = requests.post(f"{BASE_URL}/submit-review", json=payload)
if response.status_code != 200:
    print("Failed to submit review:", response.status_code)
    exit()

review_id = response.json()["review_id"]
print("Review submitted! ID:", review_id)

# Step 2: Poll for result
for attempt in range(10):
    print(f"[GET] Checking result... attempt {attempt + 1}")
    result_res = requests.get(f"{BASE_URL}/get-review/{review_id}")
    if result_res.status_code != 200:
        print("Error fetching result:", result_res.text)
        break

    result_data = result_res.json()
    if result_data["status"] == "complete":
        print("✅ Review complete!")
        print("Decision:", result_data["decision"])
        print("Video (base64, first 100 chars):", result_data["video"][:100], "...")
        break
    else:
        print("Still processing...")
        time.sleep(5)
else:
    print("❌ Timed out waiting for result.")
