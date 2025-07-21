#!/usr/bin/env python3
"""
Virtual Mouse - Modular Version
A hand gesture-controlled mouse using computer vision
"""

import cv2
import mediapipe as mp
import pyautogui
import logging
import time
import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'gestures'))

try:
    from gestures.gesture_utils import GestureDetector, CursorController, ActionHandler
    import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the virtual environment:")
    print("source venv_3.11/bin/activate")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def setup_mediapipe():
    """Initialize MediaPipe hands"""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=config.MAX_NUM_HANDS,
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
    )
    mp_drawing = mp.solutions.drawing_utils
    return hands, mp_hands, mp_drawing

def setup_camera():
    """Initialize camera"""
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise Exception("Could not open camera")
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)
    
    return cap

def setup_pyautogui():
    """Configure PyAutoGUI"""
    pyautogui.FAILSAFE = config.ENABLE_FAILSAFE
    pyautogui.PAUSE = config.PAUSE_BETWEEN_ACTIONS
    return pyautogui

def draw_debug_overlay(frame, landmarks, raw_gesture, stable_gesture, cursor_pos, gesture_detector):
    """Draw comprehensive debug information"""
    if not config.SHOW_DEBUG_INFO:
        return
    
    height, width = frame.shape[:2]
    
    # Cursor position
    if cursor_pos and config.SHOW_DEBUG_INFO:
        cv2.circle(frame, cursor_pos, 8, (0, 255, 0), -1)
        cv2.circle(frame, cursor_pos, 15, (0, 255, 0), 2)
    
    # Gesture information
    y_offset = 30
    cv2.putText(frame, f'Raw: {raw_gesture}', (10, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    y_offset += 25
    cv2.putText(frame, f'Stable: {stable_gesture}', (10, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    y_offset += 25
    
    # Hand size calibration
    if gesture_detector.hand_size_baseline:
        cv2.putText(frame, f'Hand Size: {gesture_detector.hand_size_baseline:.3f}', (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        y_offset += 20
    
    # Finger status
    if landmarks and config.SHOW_FINGER_STATUS:
        finger_states = gesture_detector.get_finger_states(landmarks)
        finger_status = ''.join([k[0].upper() if v else '-' for k, v in finger_states.items()])
        cv2.putText(frame, f'Fingers: {finger_status}', (width - 200, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Instructions
    instructions = [
        "Controls:",
        "Q - Quit",
        "R - Reset calibration",
        "Pinch - Click",
        "Peace - Right click",
        "3 fingers - Scroll up",
        "4 fingers - Scroll down",
        "Fist - Drag",
        "Open hand - Screenshot"
    ]
    
    for i, instruction in enumerate(instructions):
        cv2.putText(frame, instruction, (width - 200, height - 180 + i * 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

def main():
    """Main application loop"""
    logger = logging.getLogger(__name__)
    setup_logging()
    
    logger.info("Starting Virtual Mouse...")
    
    try:
        # Initialize components
        hands, mp_hands, mp_drawing = setup_mediapipe()
        cap = setup_camera()
        pyautogui_instance = setup_pyautogui()
        
        screen_width, screen_height = pyautogui_instance.size()
        logger.info(f"Screen resolution: {screen_width}x{screen_height}")
        
        # Create detector and controller instances
        gesture_detector = GestureDetector(
            buffer_size=config.GESTURE_BUFFER_SIZE,
            confidence_threshold=config.GESTURE_CONFIDENCE_THRESHOLD
        )
        cursor_controller = CursorController(
            smoothing_factor=config.CURSOR_SMOOTHING_FACTOR,
            acceleration_threshold=config.CURSOR_ACCELERATION_THRESHOLD
        )
        action_handler = ActionHandler(pyautogui_instance)
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(config.SCREENSHOT_DIRECTORY, exist_ok=True)
        
        logger.info("Virtual Mouse initialized successfully. Press 'q' to quit.")
        
        # Main loop
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read from camera")
                break
            
            if config.FLIP_HORIZONTAL:
                frame = cv2.flip(frame, 1)
            
            # Process frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            raw_gesture = None
            stable_gesture = None
            cursor_pos = None
            landmarks = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks if enabled
                    if config.SHOW_HAND_LANDMARKS:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get comprehensive landmarks
                    landmarks = gesture_detector.get_comprehensive_landmarks(hand_landmarks)
                    
                    # Move cursor
                    cursor_pos = cursor_controller.move_cursor(
                        landmarks['index_tip'], 
                        screen_width, 
                        screen_height, 
                        pyautogui_instance
                    )
                    
                    # Detect gestures
                    raw_gesture = gesture_detector.detect_gesture(hand_landmarks)
                    stable_gesture = gesture_detector.smooth_gesture(raw_gesture)
                    
                    # Execute actions
                    if stable_gesture and stable_gesture != 'none':
                        action_handler.execute_action(stable_gesture)
            else:
                # No hand detected - stop any ongoing drag
                action_handler.stop_drag()
            
            # Draw debug overlay
            draw_debug_overlay(frame, landmarks, raw_gesture, stable_gesture, cursor_pos, gesture_detector)
            
            # Show frame
            cv2.imshow('Virtual Mouse - Modular', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Quit requested by user")
                break
            elif key == ord('r'):
                gesture_detector.reset_calibration()
                logger.info("Calibration reset by user")
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                logger.debug(f"FPS: {fps:.1f}")
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        action_handler.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Virtual Mouse closed successfully")

if __name__ == "__main__":
    main()
