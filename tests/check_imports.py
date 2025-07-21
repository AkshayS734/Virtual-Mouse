#!/usr/bin/env python3
"""
Import verification script for Virtual Mouse project
"""

import sys
import os

# Add parent directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing Virtual Mouse Imports...")
    print("=" * 40)
    
    # Test core dependencies
    try:
        import cv2
        print("✅ OpenCV (cv2) imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
    
    try:
        import pyautogui
        print("✅ PyAutoGUI imported successfully")
    except ImportError as e:
        print(f"❌ PyAutoGUI import failed: {e}")
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
    
    # Test custom modules
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gestures'))
        
        from gestures.gesture_utils import GestureDetector, CursorController, ActionHandler
        print("✅ Custom gesture modules imported successfully")
    except ImportError as e:
        print(f"❌ Custom modules import failed: {e}")
    
    try:
        import config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config module import failed: {e}")
    
    print("\n🎯 Import Test Complete!")
    print("\nIf you see any ❌ errors above:")
    print("1. Make sure you're in the virtual environment: source venv_3.11/bin/activate")
    print("2. Install missing packages: pip install -r requirements.txt")
    print("3. Check VS Code Python interpreter points to ./venv_3.11/bin/python")
    print("\n🚀 Ready to run:")
    print("• python main.py (main implementation)")
    print("• python virtual_mouse_modular.py (modular version)")

if __name__ == "__main__":
    test_imports()
