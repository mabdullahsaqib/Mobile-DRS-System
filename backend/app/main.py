from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, json, base64
from core.InputModel import VideoAnalysisInput

from modules.ball_tracking.dummy.ball_tracking_dummy import ball_tracking_dummy
# from modules.edge_detection.src import edge_detection
# from modules.trajectory_analysis.src import trajectory_analysis
# from modules.decision_making.src import decision_making
# from modules.stream_analysis.src import stream_analysis

app = FastAPI()

@app.post("/drs-review")
async def analyze_review(input_data: VideoAnalysisInput):
    try:
        # Module 2: Ball Tracking (dummy only)
        ball_data = ball_tracking_dummy(duration_sec=15, fps=3)

        # # Module 3: Edge Detection
        # edge_result = edge_detection(ball_data)

        # # Module 4: Trajectory Analysis
        # trajectory_data = trajectory_analysis(edge_result)

        # # Module 5: Decision Making
        # final_decision = decision_making(trajectory_data)

        # # Module 6: Stream Analysis
        # result_video = stream_analysis(
        #     input_data.results, ball_data, final_decision
        # )

        # Temporary hardcoded decision & dummy video return
        result_video = ball_data  # Already base64-encoded dummy output
        final_decision = "NOT OUT"  # Placeholder decision

        return {
            "status": "complete",
            "decision": final_decision,
            "video": result_video[:5]  # base64-encoded video
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review analysis failed: {e}")
