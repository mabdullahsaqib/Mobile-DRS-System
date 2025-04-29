import cv2
import numpy as np
import base64

import cv2
import numpy as np
import base64

def combine_frames_to_video(frames):
    # Example: Create a video from frames
    frame_height = 360
    frame_width = 640
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output_video.mp4', fourcc, 30.0, (frame_width, frame_height))

    for frame in frames:
        img = base64.b64decode(frame)
        np_array = np.frombuffer(img, dtype=np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        out.write(frame)

    out.release()
    
    # Convert output video to base64
    with open('output_video.mp4', 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    return video_data

# def combine_frames_to_video(frames):
#     # Create an OpenCV video writer to save the final video
#     frame_height, frame_width, _ = frames[0].shape
#     out = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (frame_width, frame_height))

#     # Write each frame to the video
#     for frame in frames:
#         out.write(frame)
    
#     out.release()
    
#     # Convert the final video to base64 and return
#     with open('output_video.mp4', 'rb') as video_file:
#         return base64.b64encode(video_file.read()).decode('utf-8')
