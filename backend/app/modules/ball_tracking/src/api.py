
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import shutil
import os

from .main import analyze_frame, analyze_video

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ball & Object Tracking Module is Online 🚀"}

@app.post("/detect-frame/")
async def detect_from_frame(file: UploadFile = File(...)):
    """
    Upload a single frame (image) to detect ball and stumps.
    """
    temp_path = f"assets/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    frame = cv2.imread(temp_path)
    if frame is None:
        return JSONResponse(content={"error": "Failed to load image"}, status_code=400)

    results = analyze_frame(frame)  # uses main.py logic
    return JSONResponse(content=results)


@app.post("/detect-video/")
async def detect_from_video(file: UploadFile = File(...)):
    """
    Upload a video file to detect ball and stumps in first frame.
    """
    temp_path = f"assets/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = analyze_video(temp_path)  # uses main.py logic
    return JSONResponse(content=results)
