# from fastapi import FastAPI
# from fastapi.testclient import TestClient

# app = FastAPI()

def check_ball_inline(data):
    ball_frames = []

    #get all frames with ball data
    for frame in data:
        ball_data = frame.get("detections", {}).get("ball", [])
        if ball_data:
            ball_frames.append({
                "timestamp": frame["timestamp"],
                "ball_center": ball_data[0]["center"],  # (x, y)
                "ball": ball_data[0],
                "stumps": frame["detections"].get("stumps", []),
                "batsman": frame["detections"].get("batsman", [])
            })

    # select the ball frame where the ball is closest to the ground
    pitch_frame = min(ball_frames, key=lambda f: f["ball"]["z"])

    if pitch_frame:
        ball_data = pitch_frame.get("ball", {})
        stumps = pitch_frame.get("stumps", [])
        batsman = pitch_frame.get("batsman", [])

        if ball_data and stumps and batsman:
            #get batsman wrist data fr position
            keypoints = batsman[0]["keypoints"]
            lw = keypoints.get("Left Wrist")
            rw = keypoints.get("Right Wrist")
            is_right_handed = rw[0] < lw[0]

            #check ball impact position
            st_x, _, st_w, _ = stumps[0]["bbox"]
            st_left = st_x
            st_right = st_x + st_w

            #compare ball impact position with stumps
            hip_center_x = (keypoints.get("Left Hip", [0])[0] + keypoints.get("Right Hip", [0])[0]) / 2

            #check if the ball is in line with the stumps
            pitch_cx, _ = ball_data["center"]
            if (is_right_handed and pitch_cx > st_right) or (not is_right_handed and pitch_cx < st_left):
                return False

            # Check if the ball impacted the correct side
            impact_cx, _ = ball_data["center"]
            if is_right_handed:
                if impact_cx < hip_center_x:
                    return False  # offside
            else:
                if impact_cx > hip_center_x:
                    return False  # offside

            return True  # inline or leg side

    return False  # No valid frame found

def bat_edge_detect(data):
    return {"edge_detected": data['is_edge_detected']}

#computing the final decision
def final_decision(module2, module3, module4):
    inline = check_ball_inline(module2)
    edge_detected = bat_edge_detect(module3)
    will_hit_stumps = module4
    print("Inline:", inline)
    print("Edge Detected:", edge_detected)
    print("Will Hit Stumps:", will_hit_stumps)
    if not inline:
        return {"Out": False, "Reason": "not inline"}
    elif edge_detected["edge_detected"]:
        return {"Out": False, "Reason": "Bat Edge Detected"}
    elif not will_hit_stumps:
        return {"Out": False, "Reason": "Missing Wicket"}
    else:
        return {"Out": True, "Reason": "Out"}
