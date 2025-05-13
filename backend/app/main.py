from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os, json, base64, threading
from core.InputModel import VideoAnalysisInput

from modules.ball_tracking.src.main import ball_tracking
from modules.edge_detection.router import edge_detection
from modules.trajectory_analysis.tests.work import run_analysis
from modules.decision_making.FinalDecision import final_decision
from modules.stream_analysis.stream_analysis import augmented_stream

app = FastAPI()

REVIEW_DIR = "reviews/"
os.makedirs(REVIEW_DIR, exist_ok=True)  # Ensure reviews directory exists

# Background task for processing review
def process_review(review_id: str, input_path):
    try:
        review_path = os.path.join(REVIEW_DIR, review_id + "/")
        ball_tracking_output_path = os.path.join(review_path, "ball_tracking_output.json")

        module = 1

        # Module 2: Ball Tracking
        ball_data = ball_tracking(
            input_path, ball_tracking_output_path
        )

        module = 2

        # Module 3: Edge Detection
        edge_result = edge_detection(ball_data, input_path)

        module = 3

        # Module 4: Trajectory Analysis
        trajectory_data, hit  = run_analysis(ball_tracking_output_path)

        module = 4

        # Module 5: Decision Making
        decision = final_decision(
            ball_data, edge_result, hit
        )

        module = 5

        # Module 6: Stream Analysis
        result_video = augmented_stream(
            input_path, ball_data, decision
        )

        module = 6

        # Save result video
        video_path = os.path.join(review_path, "video.txt")
        with open(video_path, "w") as vf:
            vf.write(result_video)

        # Save decision
        with open(os.path.join(review_path, "decision.json"), "w") as df:
            json.dump({"decision": decision}, df)

        print(f"Review {review_id} completed successfully")

    except Exception as e:
        print(f"[ERROR] Processing failed for {review_id}: {e} (module={module})")


@app.post("/submit-review")
async def submit_review(input_data: VideoAnalysisInput):
    try:
        review_id = str(uuid4())
        review_path = os.path.join(REVIEW_DIR, review_id+ "/")
        os.makedirs(review_path, exist_ok=True)

        # Save input data
        input_path = os.path.join(review_path, "input.json")
        with open(input_path, "w") as f:
            f.write(input_data.json())

        # Start background processing
        threading.Thread(target=process_review, args=(review_id, input_path)).start()

        return {"review_id": review_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submit error: {e}")


@app.get("/get-review/{review_id}")
async def get_review_result(review_id: str):
    try:
        review_path = os.path.join(REVIEW_DIR, review_id)
        result_file = os.path.join(review_path, "decision.json")
        video_file = os.path.join(review_path, "video.txt")

        if not os.path.exists(result_file):
            return {"status": "processing"}

        with open(result_file, "r") as rf:
            decision_data = json.load(rf)

        with open(video_file, "r") as vf:
            encoded_video = vf.read()

        return {
            "status": "complete",
            "decision": decision_data["decision"],
            "video": encoded_video
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Result fetch error: {e}")
