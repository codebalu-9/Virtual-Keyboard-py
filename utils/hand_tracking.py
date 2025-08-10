import cv2
import numpy as np
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_draw = mp.solutions.drawing_utils
prev_x=None
swipe_thershold = 0.15
swipe_threshold_distance = 0.15
swipe_threshold_speed = 0.5
def detect_hand_landmarks(img, w, h):
    global prev_x, prev_time
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    index_finger = (0, 0)
    landmark_list = []
    tap = False
    thumbs_up = False
    swipe = None

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        for id, lm in enumerate(hand_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            landmark_list.append((cx, cy))
        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if len(landmark_list) > 8:
            index_finger = landmark_list[8]
            tap = is_tap(landmark_list)
            thumbs_up = is_thumbs_up(hand_landmarks.landmark)
            wrist_x = hand_landmarks.landmark[0].x
            current_time = time.time()
            if prev_x is not None and prev_time is not None:
                dx = wrist_x - prev_x
                dt = current_time - prev_time

                if abs(dx) > swipe_threshold_distance and dt < swipe_threshold_speed:
                    if dx > 0:
                        swipe = "right"
                    else:
                        swipe = "left"

            prev_x = wrist_x
            prev_time = current_time
    print("Thumbs_up:",thumbs_up,"Swipe:",swipe)
    return landmark_list, index_finger, tap, thumbs_up, swipe

def is_tap(landmarks):
    if len(landmarks) < 9:
        return False
    x1, y1 = landmarks[4]  # Thumb tip
    x2, y2 = landmarks[8]  # Index tip
    dist = np.linalg.norm(np.array([x2 - x1, y2 - y1]))
    return dist < 30

def is_thumbs_up(landmarks):
    thumb_tip_y = landmarks[4].y
    index_tip_y = landmarks[8].y
    folded_count = 0
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y > landmarks[pip].y:
            folded_count += 1
    return thumb_tip_y < index_tip_y and folded_count >= 3
def detect_swipe(landmarks):
    global prev_x
    wrist_x = landmarks[0].x
    if prev_x is None:
        prev_x = wrist_x
        return None
    diff = wrist_x - prev_x
    prev_x = wrist_x
    if diff > swipe_thershold:
        return "right"
    elif diff < -swipe_thershold:
        return "left"
    return None