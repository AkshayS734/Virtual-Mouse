# Virtual Mouse Configuration File

# Camera Settings
CAMERA_INDEX = 0
FLIP_HORIZONTAL = True
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Hand Detection Settings
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Gesture Recognition Settings
GESTURE_BUFFER_SIZE = 7
GESTURE_CONFIDENCE_THRESHOLD = 0.8

# Base Distance Thresholds (auto-scaled based on hand size)
BASE_CLICK_THRESHOLD = 0.05
BASE_RIGHT_CLICK_THRESHOLD = 0.06
BASE_SCROLL_THRESHOLD = 0.06
BASE_PINCH_THRESHOLD = 0.03

# Cursor Control Settings
CURSOR_SMOOTHING_FACTOR = 0.3  # 0 = no smoothing, 1 = maximum smoothing
CURSOR_ACCELERATION_THRESHOLD = 50  # pixels
CURSOR_DEAD_ZONE = 5  # minimum movement in pixels

# Action Cooldowns (seconds)
ACTION_COOLDOWNS = {
    'click': 0.2,
    'right_click': 0.3,
    'scroll_up': 0.1,
    'scroll_down': 0.1,
    'drag': 0.5,
    'screenshot': 2.0,
    'volume_up': 0.5,
    'volume_down': 0.5
}

# Debug Settings
SHOW_DEBUG_INFO = True
SHOW_HAND_LANDMARKS = True
SHOW_FINGER_STATUS = True
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# Performance Settings
TARGET_FPS = 30
ENABLE_GPU_ACCELERATION = False

# Security Settings
ENABLE_FAILSAFE = True  # PyAutoGUI failsafe
PAUSE_BETWEEN_ACTIONS = 0.01

# File Settings
SCREENSHOT_DIRECTORY = "./screenshots"
LOG_FILE = "virtual_mouse.log"
