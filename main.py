from utils.hand_tracking import detect_hand_landmarks, is_tap
from ui.keyboard import create_keyboard_buttons, draw_keyboard, erase_button, submit_button
from ui.platform import platform_buttons, draw_platform_buttons, detect_platform_selection
from utils.search import perform_search
from utils.hand_tracking import detect_hand_landmarks, is_tap

import cv2
import time
import pyautogui

typed_text = ""
selected_platform = "Google"
last_keypress_time = 0



buttons = create_keyboard_buttons()

# Capture video
cap = cv2.VideoCapture(0)
cv2.namedWindow("Gesture Keyboard Search", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Keyboard Search", 1000, 800)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    h, w, _ = img.shape

    landmark_list, index_finger, tap, thumbs_up, swipe = detect_hand_landmarks(img, w, h)

    if thumbs_up:
        cv2.putText(img, "SUBMIT triggered", (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        perform_search(selected_platform, typed_text)
        typed_text = ""
        time.sleep(0.3)

    if swipe == "left":
        cv2.putText(img, "DELETE triggered", (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        if len(typed_text) > 0:
            typed_text = typed_text[:-1] #Remove the last character..Balu
        time.sleep(0.3)

    if swipe == "right":
        cv2.putText(img, "SPACE triggered", (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
        typed_text += " "
        time.sleep(0.3)

    draw_platform_buttons(img, selected_platform)

    if tap:
        selected_platform = detect_platform_selection(index_finger, selected_platform)
        time.sleep(0.3)

    draw_keyboard(img, buttons)
    


    if tap:
        for btn in buttons:
            if btn.is_hover(*index_finger):
                typed_text += btn.text
                last_keypress_time = time.time()
                time.sleep(0.3)
    erase_button.draw(img)
    submit_button.draw(img)

    cv2.putText(img, f"Typed: {typed_text}", (50, 320),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 50, 255), 2)
    cv2.putText(img, f"Platform: {selected_platform}", (50, 360),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 100, 255), 2)

    if tap:
        cv2.circle(img, index_finger, 15, (0, 0, 255), cv2.FILLED)

    if tap and erase_button.is_hover(*index_finger):
        typed_text = typed_text[:-1]
        time.sleep(0.3)

    if tap and submit_button.is_hover(*index_finger):
        perform_search(selected_platform, typed_text)
        typed_text = ""
        time.sleep(0.3)

    cv2.imshow("Gesture Keyboard Search", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()