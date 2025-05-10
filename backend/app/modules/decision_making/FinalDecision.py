# from fastapi import FastAPI
# from fastapi.testclient import TestClient
from Module4 import get_combined_data


# app = FastAPI()

def check_ball_inline(data):
    ball_frames = []

    #get the ball frames
    for frame in data:
        ball_data = frame.get("detections", {}).get("ball", [])
        if ball_data:
            ball_frames.append({
                "timestamp": frame["timestamp"],
                "ball_center": ball_data[0]["center"],  # (x, y)
                "ball": ball_data[0],
                "stumps": frame["detections"].get("stumps", [])
            })

    # select the ball frame where the ball is closest to the ground
    ground_frame = min(ball_frames, key=lambda x: x["ball_center"][1], default=None)

    if ground_frame:
        ball_cx, ball_cy = ground_frame["ball_center"]
        stumps = ground_frame["stumps"]

        if not stumps:
            return {"inline": False}

      #calculate the bounding box of the stumps
        x, y, width, height = stumps[0]["bbox"]
        left = x
        top = y
        right = x + width
        bottom = y - height

        # basic check to see if the ball is within the stumps bounding box
        inline = left <= ball_cx <= right and top >= ball_cy >= bottom

        print(f"Ball impact frame timestamp: {ground_frame['timestamp']}")
        print(f"Ball center: ({ball_cx}, {ball_cy})")
        print(f"Stumps combined bbox: left={left}, top={top}, right={right}, bottom={bottom}")

        return {"inline": inline}

    # If no valid frame found
    return {"inline": False}

def bat_edge_detect(data):
    return {"edge_detected": data['is_edge_detected']}

def final_decision(module2_data, module3_data, module4_data):
    inline = check_ball_inline(module2_data)
    edge_detected = bat_edge_detect(module3_data)
    will_hit_stumps = module4_data

    print("Inline:", inline)
    print("Edge Detected:", edge_detected)
    print("Will Hit Stumps:", will_hit_stumps)

    if not inline["inline"]:
        return {"Out": False, "Reason": "Not Inline"}
    elif edge_detected["edge_detected"]:
        return {"Out": False, "Reason": "Bat Edge Detected"}
    elif not will_hit_stumps["will_hit_stumps"]:
        return {"Out": False, "Reason": "Missing Wicket"}
    else:
        return {"Out": True, "Reason": "Out"}

