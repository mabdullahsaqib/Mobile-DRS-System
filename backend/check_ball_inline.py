from fastapi import FastAPI
from fastapi.testclient import TestClient
from Module4 import app as module4_app

client = TestClient(module4_app)
app = FastAPI()
MODULE_4_URL = "http://127.0.0.1:8001/module4_combined_data"

def check_ball_inline(data):
    positions = data['ball_trajectory']['positions']
    stumps = data['stumps_data']

    # Find the first position where the ball hits the ground (y close to 0)
    impact_position = next((p for p in positions if abs(p['y']) <= 0.01), None)

    if not impact_position:
        return {'inline': False}

    x_impact = impact_position['x']
    z_impact = impact_position['z']

    stumps_x = stumps['position']['base_center']['x']
    stump_z_min = min(s['top_position']['z'] for s in stumps['individual_stumps'])
    stump_z_max = max(s['top_position']['z'] for s in stumps['individual_stumps'])

    # Check if the ball hit the ground within the x range of the stumps
    inline = (abs(x_impact - stumps_x) < 0.2) and (stump_z_min <= z_impact <= stump_z_max)

    return {'inline': inline}

def bat_edge_detect(data):
    return {"edge_detected": data['edge_detected']}

def wicket_impact(data):
    return {"will_hit_stumps": data['will_hit_stumps']}

@app.get("/finaldecision")
def final_decision():
    response = client.get(MODULE_4_URL)
    data = response.json()

    # Call the functions directly
    inline = check_ball_inline(data)
    edge_detected = bat_edge_detect(data)
    will_hit_stumps = wicket_impact(data)

    return {
        "inline": inline["inline"],
        "edge_detected": edge_detected["edge_detected"],
        "will_hit_stumps": will_hit_stumps["will_hit_stumps"]
    }