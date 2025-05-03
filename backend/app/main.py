# Example input format for /SendDataToBackend POST endpoint:
#
# {
#   "results": [
#     {
#       "frameId": 0,
#       "frameData": "string",  # base64-encoded JPEG string
#       "audioData": "string",  # base64-encoded PCM audio string
#       "cameraPosition": {
#         "x": 0,
#         "y": 0,
#         "z": 0
#       },
#       "cameraRotation": {
#         "x": 0,
#         "y": 0,
#         "z": 0
#       }
#     }
#   ]
# }

from fastapi import FastAPI
from modules.ball_tracking.router import router as ball_tracking_router
from modules.edge_detection.router import router as edge_detection_router
from modules.trajectory_analysis.router import router as trajectory_analysis_router
from modules.decision_making.router import router as decision_making_router
from modules.stream_analysis.router import router as stream_analysis_router
from core.InputModel import VideoAnalysisInput

app = FastAPI()

# Register all modules
app.include_router(ball_tracking_router, prefix="/ball_tracking", tags=["Tracking"])
app.include_router(edge_detection_router, prefix="/edge_detection", tags=["Edge Detection"])
app.include_router(trajectory_analysis_router, prefix="/trajectory_analysis", tags=["Trajectory"])
app.include_router(decision_making_router, prefix="/decision_making", tags=["Decision"])
app.include_router(stream_analysis_router, prefix="/stream_analysis", tags=["Stream"])


from fastapi import FastAPI, HTTPException
from modules.ball_tracking.router import router as ball_tracking_router
from modules.edge_detection.router import router as edge_detection_router
from modules.trajectory_analysis.router import router as trajectory_analysis_router
from modules.decision_making.router import router as decision_making_router
from modules.stream_analysis.router import router as stream_analysis_router
from core.InputModel import VideoAnalysisInput

app = FastAPI()

# Register all modules
app.include_router(ball_tracking_router, prefix="/ball_tracking", tags=["Tracking"])
app.include_router(edge_detection_router, prefix="/edge_detection", tags=["Edge Detection"])
app.include_router(trajectory_analysis_router, prefix="/trajectory_analysis", tags=["Trajectory"])
app.include_router(decision_making_router, prefix="/decision_making", tags=["Decision"])
app.include_router(stream_analysis_router, prefix="/stream_analysis", tags=["Stream"])

# endpoint to receive video+audio data from frontend
@app.post("/SendDataToBackend")
async def analyze_video(input_data: VideoAnalysisInput):
    try:
        frame_count = len(input_data.results)
        print(f"Received {frame_count} frames from frontend")

        
        # Dispatch or call internal services/modules here as needed
        # Sab modules ke function through which they will extract data from VideoAnalysisInput

        return {
            "message": "Data received successfully",
            "frames_received": frame_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
