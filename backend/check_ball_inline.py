from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/check_ball_inline")
async def check_ball_inline(request: Request):
    data = await request.json()

    positions = data['ball_trajectory']['positions']
    stumps = data['stumps_data']

    # Find the first position where the ball hits the ground (y close to 0)
    impact_position = next((p for p in positions if abs(p['y']) <= 0.01), None)

    if not impact_position:
        return JSONResponse(content={'inline': False})

    x_impact = impact_position['x']
    z_impact = impact_position['z']

    stumps_x = stumps['position']['base_center']['x']
    stump_z_min = min(s['top_position']['z'] for s in stumps['individual_stumps'])
    stump_z_max = max(s['top_position']['z'] for s in stumps['individual_stumps'])

    # Check if the ball hit the ground within the x range of the stumps
    inline = (abs(x_impact - stumps_x) < 0.2) and (stump_z_min <= z_impact <= stump_z_max)

    return JSONResponse(content={'inline': inline})


