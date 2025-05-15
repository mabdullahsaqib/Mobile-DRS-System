import requests
import base64

BASE_URL = "http://localhost:8000"  # adjust if hosted elsewhere

# Simulate dummy base64 JPEG and audio
def get_dummy_base64(content: str) -> str:
    return base64.b64encode(content.encode()).decode()

# Create one fake frame
fake_frame = {
    "frameId": 0,
    "frameData": get_dummy_base64("FAKE_JPEG_BYTES"),
    "audioData": get_dummy_base64("FAKE_AUDIO_BYTES"),
    "cameraPosition": {"x": 0.0, "y": 0.0, "z": 0.0},
    "cameraRotation": {"x": 0.0, "y": 0.0, "z": 0.0}
}

payload = {
    "results": [fake_frame] * 5  # Simulate 5 identical frames
}

print("[POST] Sending request to /drs-review...")
response = requests.post(f"{BASE_URL}/drs-review", json=payload)

if response.status_code == 200:
    res_json = response.json()
    print("✅ Response received!")
    print("Decision:", res_json.get("decision"))
    print("Video (base64 preview):", res_json.get("video", "")[:100], "...")
else:
    print("❌ Error:", response.status_code, response.text)
