from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os, json, base64, threading
from core.InputModel import VideoAnalysisInput

from modules.ball_tracking.dummy import ball_tracking_dummy
from modules.edge_detection.src import edge_detection
from modules.trajectory_analysis.src import trajectory_analysis
from modules.decision_making.src import decision_making
from modules.stream_analysis.src import stream_analysis

app = FastAPI()

REVIEW_DIR = "app/reviews"

# Background task for processing review
def process_review(review_id: str, input_data: VideoAnalysisInput):
    try:
        review_path = os.path.join(REVIEW_DIR, review_id)

        # Module 2: Ball Tracking
        ball_data = ball_tracking_dummy(input_data.results)

        # Module 3: Edge Detection
        edge_result = edge_detection(ball_data)

        # Module 4: Trajectory Analysis
        trajectory_data = trajectory_analysis(edge_result)

        # Module 5: Decision Making
        final_decision = decision_making(trajectory_data)

        # Module 6: Stream Analysis
        result_video = stream_analysis(
            input_data.results, ball_data, final_decision
        )

        # Save result video
        video_path = os.path.join(review_path, "result.mp4")
        with open(video_path, "wb") as vf:
            vf.write(base64.b64decode(result_video))

        # Save decision
        with open(os.path.join(review_path, "result.json"), "w") as df:
            json.dump({"decision": final_decision}, df)

        print(f"[✓] Review {review_id} completed successfully")

    except Exception as e:
        print(f"[ERROR] Processing failed for {review_id}: {e}")


@app.post("/submit-review")
async def submit_review(input_data: VideoAnalysisInput):
    try:
        review_id = str(uuid4())
        review_path = os.path.join(REVIEW_DIR, review_id)
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
        result_file = os.path.join(review_path, "result.json")
        video_file = os.path.join(review_path, "result.mp4")

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
