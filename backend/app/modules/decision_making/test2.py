from fastapi.testclient import TestClient
from check_ball_inline import app  # Replace with your actual FastAPI app module

client = TestClient(app)

def test_final_decision():
    # Send GET request to the final_decision endpoint
    response = client.get("/finaldecision")

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # Check if the response contains the expected keys (inline, edge_detected, will_hit_stumps)
    response_data = response.json()
    assert "inline" in response_data, "'inline' not in response"
    assert "edge_detected" in response_data, "'edge_detected' not in response"
    assert "will_hit_stumps" in response_data, "'will_hit_stumps' not in response"

    # Print the response for inspection
    print("Response from /finaldecision:", response_data)

# Run the test
test_final_decision()