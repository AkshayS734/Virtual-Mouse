import cv2
import mediapipe as mp
import pyautogui
import math
import time
import numpy as np
from collections import deque
import logging

# ========== Configuration ==========
class Config:
    # Camera settings
    CAMERA_INDEX = 0
    FLIP_HORIZONTAL = True
    
    # Hand detection settings
    MAX_NUM_HANDS = 1
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.7
    
    # Gesture settings
    MAX_BUFFER = 7  # Increased for better stability
    GESTURE_CONFIDENCE_THRESHOLD = 0.8  # 80% of buffer must agree
    
    # Distance thresholds (will be calibrated)
    BASE_CLICK_THRESHOLD = 0.05
    BASE_RIGHT_CLICK_THRESHOLD = 0.06
    BASE_SCROLL_THRESHOLD = 0.06
    
    # Action cooldowns (seconds)
    COOLDOWNS = {
        'click': 0.3,
        'right_click': 0.5,
        'scroll_up': 0.1,
        'scroll_down': 0.1,
        'drag_start': 0.5,
        'drag_end': 0.5,
        'screenshot': 3.0
    }
    
    # Cursor smoothing
    CURSOR_SMOOTHING = 0.3  # 0 = no smoothing, 1 = maximum smoothing

# ========== Setup ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=Config.MAX_NUM_HANDS,
        min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
    )
    mp_drawing = mp.solutions.drawing_utils
    
    # Disable PyAutoGUI failsafe for smoother operation
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.01
    
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)
    if not cap.isOpened():
        raise Exception("Could not open camera")
        
    screen_width, screen_height = pyautogui.size()
    logger.info(f"Screen resolution: {screen_width}x{screen_height}")
    
except Exception as e:
    logger.error(f"Setup failed: {e}")
    exit(1)

# ========== State Variables ==========
class MouseState:
    def __init__(self):
        self.prev_action = None
        self.last_action_time = 0
        self.prev_x, self.prev_y = 0, 0
        self.gesture_buffer = deque(maxlen=Config.MAX_BUFFER)
        self.is_dragging = False
        self.hand_size_baseline = None
        self.thresholds = {}
        
state = MouseState()

# ========== Enhanced Functions ==========

def get_landmarks(hand_landmarks):
    """Extract all relevant hand landmarks"""
    return {
        'thumb_tip': hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        'thumb_mcp': hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP],
        'index_tip': hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        'index_mcp': hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP],
        'middle_tip': hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        'middle_mcp': hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
        'ring_tip': hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
        'ring_mcp': hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP],
        'pinky_tip': hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP],
        'pinky_mcp': hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP],
        'wrist': hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    }

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two landmarks"""
    return math.hypot(point1.x - point2.x, point1.y - point2.y)

def calibrate_hand_size(landmarks):
    """Calibrate thresholds based on hand size"""
    global state
    
    # Use wrist to middle finger MCP as baseline hand size
    hand_size = calculate_distance(landmarks['wrist'], landmarks['middle_mcp'])
    
    if state.hand_size_baseline is None:
        state.hand_size_baseline = hand_size
    else:
        # Smooth the baseline to avoid sudden changes
        state.hand_size_baseline = 0.9 * state.hand_size_baseline + 0.1 * hand_size
    
    # Scale thresholds based on hand size
    scale_factor = hand_size / 0.15  # Assuming 0.15 as average hand size
    state.thresholds = {
        'click': Config.BASE_CLICK_THRESHOLD * scale_factor,
        'right_click': Config.BASE_RIGHT_CLICK_THRESHOLD * scale_factor,
        'scroll': Config.BASE_SCROLL_THRESHOLD * scale_factor
    }

def is_finger_extended(tip_landmark, mcp_landmark):
    """Check if a finger is extended by comparing tip and MCP positions"""
    return tip_landmark.y < mcp_landmark.y

def move_cursor(index_tip):
    """Enhanced cursor movement with smoothing"""
    global state
    
    curr_x = int(index_tip.x * screen_width)
    curr_y = int(index_tip.y * screen_height)
    
    # Apply smoothing
    if state.prev_x == 0 and state.prev_y == 0:
        smooth_x, smooth_y = curr_x, curr_y
    else:
        smooth_x = int(state.prev_x + (curr_x - state.prev_x) * (1 - Config.CURSOR_SMOOTHING))
        smooth_y = int(state.prev_y + (curr_y - state.prev_y) * (1 - Config.CURSOR_SMOOTHING))
    
    try:
        pyautogui.moveTo(smooth_x, smooth_y)
    except Exception as e:
        logger.warning(f"Cursor movement failed: {e}")
    
    state.prev_x, state.prev_y = smooth_x, smooth_y
    return smooth_x, smooth_y

def detect_gesture(landmarks):
    """Enhanced gesture detection with multiple gestures"""
    
    # Calibrate thresholds based on hand size
    calibrate_hand_size(landmarks)
    
    # Calculate distances
    distances = {
        'thumb_index': calculate_distance(landmarks['thumb_tip'], landmarks['index_tip']),
        'index_middle': calculate_distance(landmarks['index_tip'], landmarks['middle_tip']),
        'middle_ring': calculate_distance(landmarks['middle_tip'], landmarks['ring_tip']),
        'ring_pinky': calculate_distance(landmarks['ring_tip'], landmarks['pinky_tip']),
        'index_ring': calculate_distance(landmarks['index_tip'], landmarks['ring_tip']),
        'index_pinky': calculate_distance(landmarks['index_tip'], landmarks['pinky_tip'])
    }
    
    # Check finger extensions
    fingers_extended = {
        'thumb': landmarks['thumb_tip'].x > landmarks['thumb_mcp'].x,  # Thumb is special
        'index': is_finger_extended(landmarks['index_tip'], landmarks['index_mcp']),
        'middle': is_finger_extended(landmarks['middle_tip'], landmarks['middle_mcp']),
        'ring': is_finger_extended(landmarks['ring_tip'], landmarks['ring_mcp']),
        'pinky': is_finger_extended(landmarks['pinky_tip'], landmarks['pinky_mcp'])
    }
    
    # Gesture detection logic
    
    # 1. Click: Thumb and Index close together, others extended
    if (distances['thumb_index'] < state.thresholds['click'] and 
        fingers_extended['middle'] and fingers_extended['ring']):
        return 'click'
    
    # 2. Right Click: Index and Middle close, others extended
    if (distances['index_middle'] < state.thresholds['click'] and
        fingers_extended['ring'] and fingers_extended['pinky']):
        return 'right_click'
    
    # 3. Scroll Up: Index, Middle, Ring close (three fingers)
    if (distances['index_middle'] < state.thresholds['scroll'] and
        distances['middle_ring'] < state.thresholds['scroll'] and
        fingers_extended['pinky']):
        return 'scroll_up'
    
    # 4. Scroll Down: Ring and Pinky close, others extended
    if (distances['ring_pinky'] < state.thresholds['scroll'] and
        fingers_extended['index'] and fingers_extended['middle']):
        return 'scroll_down'
    
    # 5. Drag Start: All fingers closed (fist)
    if not any(fingers_extended.values()):
        return 'drag_start'
    
    # 6. Screenshot: All fingers extended (open hand)
    if all(fingers_extended.values()):
        return 'screenshot'
    
    # 7. No gesture detected
    return 'none'

def smoothed_gesture(new_gesture):
    """Improved gesture smoothing with confidence threshold"""
    global state
    
    state.gesture_buffer.append(new_gesture)
    
    if len(state.gesture_buffer) < Config.MAX_BUFFER:
        return None
    
    # Count occurrences of each gesture
    gesture_counts = {}
    for gesture in state.gesture_buffer:
        gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
    
    # Find the most common gesture
    most_common_gesture = max(gesture_counts, key=gesture_counts.get)
    confidence = gesture_counts[most_common_gesture] / len(state.gesture_buffer)
    
    # Return gesture only if confidence is above threshold
    if confidence >= Config.GESTURE_CONFIDENCE_THRESHOLD and most_common_gesture != 'none':
        return most_common_gesture
    
    return None

def handle_actions(action):
    """Enhanced action handling with better cooldown management"""
    global state
    
    current_time = time.time()
    cooldown = Config.COOLDOWNS.get(action, 1.0)
    
    # Check if enough time has passed since last action of this type
    if (action == state.prev_action and 
        (current_time - state.last_action_time) < cooldown):
        return
    
    try:
        if action == 'click':
            if not state.is_dragging:
                pyautogui.click()
                logger.info("Click performed")
                
        elif action == 'right_click':
            if not state.is_dragging:
                pyautogui.rightClick()
                logger.info("Right click performed")
                
        elif action == 'scroll_up':
            pyautogui.scroll(3)
            logger.info("Scroll up")
            
        elif action == 'scroll_down':
            pyautogui.scroll(-3)
            logger.info("Scroll down")
            
        elif action == 'drag_start':
            if not state.is_dragging:
                pyautogui.mouseDown()
                state.is_dragging = True
                logger.info("Drag started")
                
        elif action == 'drag_end':
            if state.is_dragging:
                pyautogui.mouseUp()
                state.is_dragging = False
                logger.info("Drag ended")
                
        elif action == 'screenshot':
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot = pyautogui.screenshot()
            screenshot.save(f"screenshot_{timestamp}.png")
            logger.info(f"Screenshot saved: screenshot_{timestamp}.png")
        
        state.prev_action = action
        state.last_action_time = current_time
        
    except Exception as e:
        logger.error(f"Action '{action}' failed: {e}")

def draw_debug_info(frame, landmarks, action_raw, action_stable, cursor_pos):
    """Draw comprehensive debug information"""
    height, width = frame.shape[:2]
    
    # Draw cursor position
    if cursor_pos:
        cv2.circle(frame, cursor_pos, 8, (0, 255, 0), -1)
        cv2.circle(frame, cursor_pos, 12, (0, 255, 0), 2)
    
    # Draw gesture info
    y_offset = 30
    cv2.putText(frame, f'Raw: {action_raw}', (10, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    y_offset += 25
    cv2.putText(frame, f'Stable: {action_stable}', (10, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    y_offset += 25
    
    # Draw hand size info
    if state.hand_size_baseline:
        cv2.putText(frame, f'Hand Size: {state.hand_size_baseline:.3f}', (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        y_offset += 20
    
    # Draw drag status
    if state.is_dragging:
        cv2.putText(frame, 'DRAGGING', (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Draw finger status
    if landmarks:
        fingers_extended = {
            'T': landmarks['thumb_tip'].x > landmarks['thumb_mcp'].x,
            'I': is_finger_extended(landmarks['index_tip'], landmarks['index_mcp']),
            'M': is_finger_extended(landmarks['middle_tip'], landmarks['middle_mcp']),
            'R': is_finger_extended(landmarks['ring_tip'], landmarks['ring_mcp']),
            'P': is_finger_extended(landmarks['pinky_tip'], landmarks['pinky_mcp'])
        }
        
        finger_status = ''.join([k if v else '-' for k, v in fingers_extended.items()])
        cv2.putText(frame, f'Fingers: {finger_status}', (width - 200, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# ========== Main Loop ==========

def main():
    """Main application loop with error handling"""
    global state
    
    logger.info("Virtual Mouse started. Press 'q' to quit, 'r' to reset calibration.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read from camera")
                break
            
            if Config.FLIP_HORIZONTAL:
                frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            action_raw = None
            action_stable = None
            cursor_pos = None
            landmarks = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get landmarks and move cursor
                    landmarks = get_landmarks(hand_landmarks)
                    cursor_pos = move_cursor(landmarks['index_tip'])
                    
                    # Detect and handle gestures
                    action_raw = detect_gesture(landmarks)
                    action_stable = smoothed_gesture(action_raw)
                    
                    if action_stable:
                        handle_actions(action_stable)
            else:
                # No hand detected - end drag if active
                if state.is_dragging:
                    handle_actions('drag_end')
            
            # Draw debug information
            draw_debug_info(frame, landmarks, action_raw, action_stable, cursor_pos)
            
            # Show frame
            cv2.imshow('Virtual Mouse - Enhanced', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset calibration
                state.hand_size_baseline = None
                state.gesture_buffer.clear()
                logger.info("Calibration reset")
                
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        if state.is_dragging:
            pyautogui.mouseUp()
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Application closed")

if __name__ == "__main__":
    main()
