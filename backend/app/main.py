from fastapi import FastAPI
from modules.ball_tracking.router import router as ball_tracking_router
from modules.edge_detection.router import router as edge_detection_router
from modules.trajectory_analysis.service import analyze_trajectory
from modules.decision_making.router import router as decision_making_router
from modules.stream_analysis.router import router as stream_analysis_router

app = FastAPI()

# Register all modules
app.include_router(ball_tracking_router, prefix="/ball_tracking", tags=["Tracking"])
app.include_router(edge_detection_router, prefix="/edge_detection", tags=["Edge Detection"])
#app.include_router(trajectory_analysis_router, prefix="/trajectory_analysis", tags=["Trajectory"])
app.include_router(decision_making_router, prefix="/decision_making", tags=["Decision"])
app.include_router(stream_analysis_router, prefix="/stream_analysis", tags=["Stream"])
