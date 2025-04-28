# test_traditional_video.py
import cv2
import numpy as np

VIDEO_PATH = 'v1.mp4'

# your tuned yellow‑ball HSV
LOWER = np.array([25, 150, 150], dtype=np.uint8)
UPPER = np.array([35, 255, 255], dtype=np.uint8)
MIN_RADIUS = 10

# stump filters
ASPECT_MIN, ASPECT_MAX = 1.8, 7.0
HEIGHT_MIN, HEIGHT_MAX = 50, 200

def detect_traditional(frame):
    dets = {'ball': [], 'stumps': []}

    # — Ball —
    hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER, UPPER)
    mask = cv2.erode(mask,  None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        c = max(cnts, key=cv2.contourArea)
        (x,y),r = cv2.minEnclosingCircle(c)
        if r > MIN_RADIUS:
            dets['ball'].append((int(x-r),int(y-r),int(2*r),int(2*r)))

    # — Stumps (improved) —
    # first get a white mask to isolate stumps (they’re cream/white)
    white_mask = cv2.inRange(hsv, (0,0,200), (180,30,255))
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN,
                                  np.ones((5,5),np.uint8))
    cnts,_ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w==0: continue
        ar = h/float(w)
        if ASPECT_MIN<ar<ASPECT_MAX and HEIGHT_MIN<h<HEIGHT_MAX:
            dets['stumps'].append((x,y,w,h))

    return dets

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        dets = detect_traditional(frame)
        # draw ball = red
        for x,y,w,h in dets['ball']:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        # draw stumps = yellow
        for x,y,w,h in dets['stumps']:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)

        cv2.imshow("Traditional Detection", frame)
        if cv2.waitKey(30)&0xFF==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
