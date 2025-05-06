from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.InputModel import VideoAnalysisInput

from modules.ball_tracking.service import run_ball_tracking
from modules.edge_detection.service import run_edge_detection
from modules.trajectory_analysis.service import run_trajectory_analysis
from modules.decision_making.service import run_decision_making
from modules.stream_analysis.service import run_stream_analysis

app = FastAPI()

@app.post("/SendDataToBackend")
async def analyze_video(input_data: VideoAnalysisInput):
    try:
        frame_count = len(input_data.results)
        print(f"[INFO] Received {frame_count} frames from frontend")

        # === Module 2: Ball Tracking ===
        ball_data = run_ball_tracking(input_data.results)
        print("[✓] Ball tracking complete")

        # === Module 3: Edge Detection ===
        edge_result = run_edge_detection(ball_data)
        print("[✓] Edge detection complete")

        # === Module 4: Trajectory Analysis ===
        trajectory_data = run_trajectory_analysis(edge_result)
        print("[✓] Trajectory analysis complete")

        # === Module 5: Decision Making ===
        final_decision = run_decision_making(trajectory_data)
        print("[✓] Final decision:", final_decision)

        # === Module 6: Stream Analysis (Video + Final Decision) ===
        response_video_base64 = run_stream_analysis(
            input_data.results,
            ball_data,
            final_decision
        )
        print("[✓] Stream analysis complete, returning response")

        return {
            "status": "success",
            "decision": final_decision,
            "video": response_video_base64  # base64-encoded video string
        }

    except Exception as e:
        print("[ERROR]", str(e))
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
