import math
import mediapipe as mp
from collections import deque
import logging

logger = logging.getLogger(__name__)

class GestureDetector:
    """Advanced gesture detection class with calibration and multiple gesture support"""
    
    def __init__(self, buffer_size=7, confidence_threshold=0.8):
        self.mp_hands = mp.solutions.hands
        self.buffer_size = buffer_size
        self.confidence_threshold = confidence_threshold
        self.gesture_buffer = deque(maxlen=buffer_size)
        self.hand_size_baseline = None
        self.thresholds = {}
        
        # Base thresholds (will be scaled)
        self.base_thresholds = {
            'click': 0.05,
            'right_click': 0.06,
            'scroll': 0.06,
            'pinch': 0.03
        }
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two landmarks"""
        return math.hypot(point1.x - point2.x, point1.y - point2.y)
    
    def get_comprehensive_landmarks(self, hand_landmarks):
        """Extract comprehensive hand landmarks"""
        landmarks = {}
        
        # All fingertips
        for finger, landmark_id in [
            ('thumb', self.mp_hands.HandLandmark.THUMB_TIP),
            ('index', self.mp_hands.HandLandmark.INDEX_FINGER_TIP),
            ('middle', self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP),
            ('ring', self.mp_hands.HandLandmark.RING_FINGER_TIP),
            ('pinky', self.mp_hands.HandLandmark.PINKY_TIP)
        ]:
            landmarks[f'{finger}_tip'] = hand_landmarks.landmark[landmark_id]
        
        # All MCPs (metacarpophalangeal joints)
        for finger, landmark_id in [
            ('thumb', self.mp_hands.HandLandmark.THUMB_MCP),
            ('index', self.mp_hands.HandLandmark.INDEX_FINGER_MCP),
            ('middle', self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
            ('ring', self.mp_hands.HandLandmark.RING_FINGER_MCP),
            ('pinky', self.mp_hands.HandLandmark.PINKY_MCP)
        ]:
            landmarks[f'{finger}_mcp'] = hand_landmarks.landmark[landmark_id]
        
        # Wrist
        landmarks['wrist'] = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        return landmarks
    
    def calibrate_hand_size(self, landmarks):
        """Dynamically calibrate thresholds based on hand size"""
        # Use wrist to middle finger MCP as hand size reference
        hand_size = self.calculate_distance(landmarks['wrist'], landmarks['middle_mcp'])
        
        if self.hand_size_baseline is None:
            self.hand_size_baseline = hand_size
        else:
            # Smooth the baseline
            self.hand_size_baseline = 0.9 * self.hand_size_baseline + 0.1 * hand_size
        
        # Scale thresholds
        scale_factor = hand_size / 0.15  # Normalized baseline
        self.thresholds = {k: v * scale_factor for k, v in self.base_thresholds.items()}
    
    def is_finger_extended(self, tip_landmark, mcp_landmark):
        """Check if finger is extended"""
        return tip_landmark.y < mcp_landmark.y
    
    def get_finger_states(self, landmarks):
        """Get the state of all fingers (extended/closed)"""
        return {
            'thumb': landmarks['thumb_tip'].x > landmarks['thumb_mcp'].x,  # Thumb logic is different
            'index': self.is_finger_extended(landmarks['index_tip'], landmarks['index_mcp']),
            'middle': self.is_finger_extended(landmarks['middle_tip'], landmarks['middle_mcp']),
            'ring': self.is_finger_extended(landmarks['ring_tip'], landmarks['ring_mcp']),
            'pinky': self.is_finger_extended(landmarks['pinky_tip'], landmarks['pinky_mcp'])
        }
    
    def detect_gesture(self, hand_landmarks):
        """Main gesture detection method"""
        landmarks = self.get_comprehensive_landmarks(hand_landmarks)
        self.calibrate_hand_size(landmarks)
        
        # Calculate key distances
        distances = {
            'thumb_index': self.calculate_distance(landmarks['thumb_tip'], landmarks['index_tip']),
            'index_middle': self.calculate_distance(landmarks['index_tip'], landmarks['middle_tip']),
            'middle_ring': self.calculate_distance(landmarks['middle_tip'], landmarks['ring_tip']),
            'ring_pinky': self.calculate_distance(landmarks['ring_tip'], landmarks['pinky_tip']),
            'thumb_middle': self.calculate_distance(landmarks['thumb_tip'], landmarks['middle_tip'])
        }
        
        finger_states = self.get_finger_states(landmarks)
        
        # Gesture recognition logic
        
        # 1. Pinch (Thumb + Index): Most precise for clicking
        if distances['thumb_index'] < self.thresholds['pinch']:
            return 'click'
        
        # 2. Peace sign (Index + Middle extended, others closed): Right click
        if (finger_states['index'] and finger_states['middle'] and 
            not finger_states['ring'] and not finger_states['pinky']):
            return 'right_click'
        
        # 3. Three fingers (Index + Middle + Ring): Scroll up
        if (finger_states['index'] and finger_states['middle'] and 
            finger_states['ring'] and not finger_states['pinky']):
            return 'scroll_up'
        
        # 4. Four fingers (all except thumb): Scroll down
        if (finger_states['index'] and finger_states['middle'] and 
            finger_states['ring'] and finger_states['pinky'] and not finger_states['thumb']):
            return 'scroll_down'
        
        # 5. Closed fist: Drag
        if not any(finger_states.values()):
            return 'drag'
        
        # 6. Open hand (all fingers): Screenshot
        if all(finger_states.values()):
            return 'screenshot'
        
        # 7. L-shape (Thumb + Index extended): Volume up
        if (finger_states['thumb'] and finger_states['index'] and 
            not finger_states['middle'] and not finger_states['ring'] and not finger_states['pinky']):
            return 'volume_up'
        
        return 'none'
    
    def smooth_gesture(self, raw_gesture):
        """Apply temporal smoothing to gestures"""
        self.gesture_buffer.append(raw_gesture)
        
        if len(self.gesture_buffer) < self.buffer_size:
            return None
        
        # Count gesture occurrences
        gesture_counts = {}
        for gesture in self.gesture_buffer:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        # Find most common gesture
        most_common = max(gesture_counts, key=gesture_counts.get)
        confidence = gesture_counts[most_common] / len(self.gesture_buffer)
        
        if confidence >= self.confidence_threshold and most_common != 'none':
            return most_common
        
        return None
    
    def reset_calibration(self):
        """Reset hand size calibration"""
        self.hand_size_baseline = None
        self.gesture_buffer.clear()
        logger.info("Gesture detector calibration reset")


class CursorController:
    """Enhanced cursor control with smoothing and acceleration"""
    
    def __init__(self, smoothing_factor=0.3, acceleration_threshold=50):
        self.prev_x = 0
        self.prev_y = 0
        self.smoothing_factor = smoothing_factor
        self.acceleration_threshold = acceleration_threshold
        self.velocity_x = 0
        self.velocity_y = 0
    
    def move_cursor(self, landmark, screen_width, screen_height, pyautogui_instance):
        """Move cursor with advanced smoothing and acceleration"""
        import time
        
        target_x = int(landmark.x * screen_width)
        target_y = int(landmark.y * screen_height)
        
        if self.prev_x == 0 and self.prev_y == 0:
            # First movement
            self.prev_x, self.prev_y = target_x, target_y
            smooth_x, smooth_y = target_x, target_y
        else:
            # Calculate movement distance
            distance = math.hypot(target_x - self.prev_x, target_y - self.prev_y)
            
            # Apply acceleration for large movements
            if distance > self.acceleration_threshold:
                acceleration_factor = min(2.0, distance / self.acceleration_threshold)
                smoothing = self.smoothing_factor / acceleration_factor
            else:
                smoothing = self.smoothing_factor
            
            # Smooth movement
            smooth_x = int(self.prev_x + (target_x - self.prev_x) * (1 - smoothing))
            smooth_y = int(self.prev_y + (target_y - self.prev_y) * (1 - smoothing))
        
        try:
            pyautogui_instance.moveTo(smooth_x, smooth_y)
            self.prev_x, self.prev_y = smooth_x, smooth_y
            return smooth_x, smooth_y
        except Exception as e:
            logger.warning(f"Cursor movement failed: {e}")
            return self.prev_x, self.prev_y


class ActionHandler:
    """Handle various mouse and system actions"""
    
    def __init__(self, pyautogui_instance):
        self.pyautogui = pyautogui_instance
        self.last_action_times = {}
        self.is_dragging = False
        
        self.cooldowns = {
            'click': 0.2,
            'right_click': 0.3,
            'scroll_up': 0.1,
            'scroll_down': 0.1,
            'drag': 0.5,
            'screenshot': 2.0,
            'volume_up': 0.5
        }
    
    def can_execute_action(self, action):
        """Check if enough time has passed to execute action"""
        import time
        current_time = time.time()
        last_time = self.last_action_times.get(action, 0)
        cooldown = self.cooldowns.get(action, 0.5)
        
        return (current_time - last_time) >= cooldown
    
    def execute_action(self, action):
        """Execute the specified action"""
        import time
        import subprocess
        
        if not self.can_execute_action(action):
            return False
        
        try:
            if action == 'click':
                if not self.is_dragging:
                    self.pyautogui.click()
                    logger.info("Click executed")
            
            elif action == 'right_click':
                if not self.is_dragging:
                    self.pyautogui.rightClick()
                    logger.info("Right click executed")
            
            elif action == 'scroll_up':
                self.pyautogui.scroll(3)
                logger.info("Scroll up")
            
            elif action == 'scroll_down':
                self.pyautogui.scroll(-3)
                logger.info("Scroll down")
            
            elif action == 'drag':
                if not self.is_dragging:
                    self.pyautogui.mouseDown()
                    self.is_dragging = True
                    logger.info("Drag started")
            
            elif action == 'screenshot':
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                screenshot = self.pyautogui.screenshot()
                screenshot.save(f"screenshot_{timestamp}.png")
                logger.info(f"Screenshot saved: screenshot_{timestamp}.png")
            
            elif action == 'volume_up':
                # macOS volume control
                try:
                    subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) + 10)'])
                    logger.info("Volume increased")
                except:
                    logger.warning("Volume control failed")
            
            self.last_action_times[action] = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return False
    
    def stop_drag(self):
        """Stop dragging if active"""
        if self.is_dragging:
            try:
                self.pyautogui.mouseUp()
                self.is_dragging = False
                logger.info("Drag stopped")
            except Exception as e:
                logger.error(f"Failed to stop drag: {e}")
    
    def cleanup(self):
        """Cleanup method to ensure drag is stopped"""
        self.stop_drag()