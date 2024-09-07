import cv2
import mediapipe as mp
import pyautogui
import math


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

screen_width, screen_height = pyautogui.size()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
           
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

           
            screen_x = int(index_finger_tip.x * screen_width)
            screen_y = int(index_finger_tip.y * screen_height)

        
            pyautogui.moveTo(screen_x, screen_y)

            distance_click= math.hypot(index_finger_tip.x - middle_finger_tip.x, index_finger_tip.y - middle_finger_tip.y)
            distance_scroll= math.hypot(middle_finger_tip.x - ring_finger_tip.x, middle_finger_tip.y - ring_finger_tip.y)
            distance_scroll_down= math.hypot(ring_finger_tip.x - pinky_tip.x, ring_finger_tip.y - pinky_tip.y)

            
            if distance_click < 0.1: 
                pyautogui.click()
            if (distance_click<0.1 and distance_scroll<0.1):
                pyautogui.scroll(10)
            if (distance_click<0.1 and distance_scroll_down<0.1):
                pyautogui.scroll(-10) 
            if distance_click > 0.1: 
                pyautogui.screenshot()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.imshow('Virtual Mouse', frame)

cap.release()
cv2.destroyAllWindows()
