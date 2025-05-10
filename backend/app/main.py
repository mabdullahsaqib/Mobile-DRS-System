from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os, json, base64, threading
from core.InputModel import VideoAnalysisInput

from modules.ball_tracking.dummy.ball_tracking_dummy import ball_tracking_dummy
from modules.edge_detection.router import edge_detection
from modules.trajectory_analysis.tests.work import run_analysis
from modules.decision_making.FinalDecision import final_decision
from modules.stream_analysis.stream_analysis import augmented_stream

app = FastAPI()

REVIEW_DIR = "reviews/"
os.makedirs(REVIEW_DIR, exist_ok=True)  # Ensure reviews directory exists

# Background task for processing review
def process_review(review_id: str, input_data: VideoAnalysisInput):
    try:
        review_path = os.path.join(REVIEW_DIR, review_id + "/")

        # Module 2: Ball Tracking
        ball_data = ball_tracking_dummy(duration_sec=15, fps=30)
        with open("dummy_module2_output.json", "w") as f:
            json.dump(ball_data, f, indent=2)

        # Module 3: Edge Detection
        edge_result = edge_detection(ball_data)

        # Module 4: Trajectory Analysis
        trajectory_data, hit  = run_analysis(ball_data)

        # Module 5: Decision Making
        decision = final_decision(
            ball_data, edge_result, hit
        )

        # Module 6: Stream Analysis
        result_video = augmented_stream(
            input_data.results, ball_data, decision
        )

        # Save result video
        video_path = os.path.join(review_path, "video.txt")
        with open(video_path, "wb") as vf:
            vf.write(result_video)

        # Save decision
        with open(os.path.join(review_path, "decision.json"), "w") as df:
            json.dump({"decision": decision}, df)

        print(f"Review {review_id} completed successfully")

    except Exception as e:
        print(f"[ERROR] Processing failed for {review_id}: {e}")


@app.post("/submit-review")
async def submit_review(input_data: VideoAnalysisInput):
    try:
        review_id = str(uuid4())
        review_path = os.path.join(REVIEW_DIR, review_id+ "/")
        os.makedirs(review_path, exist_ok=True)

        # Save input data
        with open(os.path.join(review_path, "input.json"), "w") as f:
            f.write(input_data.json())

        # Start background processing
        threading.Thread(target=process_review, args=(review_id, input_data)).start()

        return {"review_id": review_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submit error: {e}")


@app.get("/review-result/{review_id}")
async def get_review_result(review_id: str):
    try:
        review_path = os.path.join(REVIEW_DIR, review_id)
        result_file = os.path.join(review_path, "decision.json")
        video_file = os.path.join(review_path, "video.txt")

        if not os.path.exists(result_file):
            return {"status": "processing"}

        with open(result_file, "r") as rf:
            decision_data = json.load(rf)

        with open(video_file, "rb") as vf:
            encoded_video = base64.b64encode(vf.read()).decode("utf-8")

        return {
            "status": "complete",
            "decision": decision_data["decision"],
            "video": encoded_video
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Result fetch error: {e}")
