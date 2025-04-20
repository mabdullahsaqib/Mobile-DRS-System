from fastapi.testclient import TestClient
from check_ball_inline import app  # Adjust this import to your actual file name if needed

client = TestClient(app)

def test_check_ball_inline():
    # Updated JSON data simulating 5 ball positions
    json_data = {

        #for true inline check

        # "ball_trajectory": {
        #     "positions": [
        #         {"x": 4, "y": 1.2, "z": 5.0},
        #         {"x": 5, "y": 0.9, "z": 5.5},
        #         {"x": 6, "y": 0.6, "z": 6.0},
        #         {"x": 7, "y": 0.3, "z": 6.5},
        #         {"x": 8, "y": 0.01, "z": 6.8}  # Impact point (y ~ 0)
        #     ]
        # },
        # "stumps_data": {
        #     "position": {
        #         "base_center": {"x": 8}
        #     },
        #     "individual_stumps": [
        #         {"top_position": {"x": 8, "y": 0.71, "z": 6.7}},
        #         {"top_position": {"x": 8, "y": 0.71, "z": 6.8}},
        #         {"top_position": {"x": 8, "y": 0.71, "z": 6.9}}
        #     ]
        # }

        #for false inline check
        "ball_trajectory": {
            "positions": [
                {"x": 4, "y": 1.2, "z": 5.0},
                {"x": 5, "y": 0.9, "z": 5.2},
                {"x": 6, "y": 0.6, "z": 5.0},
                {"x": 7, "y": 0.3, "z": 4.7},
                {"x": 8, "y": 0.01, "z": 4.5}  # Impact point: x = 8, z = 4.5
            ]
        },
        "stumps_data": {
            "position": {
                "base_center": {"x": 8}
            },
            "individual_stumps": [
                {"top_position": {"x": 8, "y": 0.71, "z": 6.7}},
                {"top_position": {"x": 8, "y": 0.71, "z": 6.8}},
                {"top_position": {"x": 8, "y": 0.71, "z": 6.9}}
            ]
        }
    }

    # Send POST request
    response = client.post("/check_ball_inline", json=json_data)

    # Check and print response
    assert response.status_code == 200
    print("Test Output:", response.json())

# Run the test
test_check_ball_inline()
