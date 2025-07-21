# 🖱️ Virtual Mouse

**Control your computer with hand gestures using computer vision**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)

Virtual Mouse is a computer vision project that lets you control your mouse cursor and perform various actions using simple hand gestures. No need for a physical mouse - just use your webcam and hand movements!

## ✨ Features

- 🎯 **Precise cursor control** with hand tracking
- 👆 **Multiple gesture support** (click, right-click, scroll, drag)
- 🔧 **Auto-calibration** adapts to your hand size
- 🚀 **Real-time processing** with smooth performance
- 🛡️ **Error handling** with graceful failure recovery
- ⚙️ **Configurable settings** for personalization
- 📱 **Cross-platform** support (Windows, macOS, Linux)

## � Gesture Controls

| Gesture | Action | How to Perform |
|---------|---------|----------------|
| 👌 **Pinch** | Left Click | Touch thumb and index finger together |
| ✌️ **Peace Sign** | Right Click | Show index and middle fingers only |
| 🤟 **Three Fingers** | Scroll Up | Extend index, middle, and ring fingers |
| 🖐️ **Four Fingers** | Scroll Down | Extend all fingers except thumb |
| ✊ **Closed Fist** | Drag | Make a fist to drag objects |
| 🖐️ **Open Hand** | Screenshot | Show all five fingers |

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Webcam
- Good lighting conditions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AkshayS734/virtual-mouse.git
   cd virtual-mouse
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

That's it! Your webcam should open and you can start controlling your mouse with hand gestures.

## � System Requirements

### Minimum Requirements
- **CPU**: Dual-core processor
- **RAM**: 4GB
- **Camera**: Any USB webcam or built-in camera
- **OS**: Windows 7+, macOS 10.12+, or Linux

### Recommended
- **CPU**: Quad-core processor
- **RAM**: 8GB
- **Camera**: HD webcam for better accuracy
- **Lighting**: Well-lit environment

## 🎯 Usage Guide

### First Time Setup

1. **Position yourself**: Sit 1-2 feet away from your camera
2. **Check lighting**: Ensure your hand is well-lit
3. **Start the app**: Run `python main.py`
4. **Calibrate**: The app will automatically adjust to your hand size

### Basic Usage

1. **Move cursor**: Point with your index finger
2. **Click**: Make a pinch gesture (thumb + index)
3. **Right-click**: Show peace sign (index + middle)
4. **Scroll**: Use three fingers (up) or four fingers (down)
5. **Drag**: Make a fist and move your hand
6. **Screenshot**: Show all five fingers

### Keyboard Controls

- **Q**: Quit the application
- **R**: Reset hand calibration

### Tips for Best Performance

- 🔆 Use good lighting
- 📏 Stay 1-2 feet from camera
- 🤚 Make clear, distinct gestures
- ⏱️ Hold gestures for 1-2 seconds
- 🔄 Press 'R' if gestures aren't recognized

## ⚙️ Configuration

You can customize the app by editing `config.py`:

```python
# Gesture sensitivity (0.1 to 1.0)
GESTURE_CONFIDENCE_THRESHOLD = 0.8

# Cursor smoothing (0 = no smoothing, 1 = max smoothing)
CURSOR_SMOOTHING_FACTOR = 0.3

# Camera settings
CAMERA_INDEX = 0  # Change if you have multiple cameras
FLIP_HORIZONTAL = True  # Mirror the video feed
```

## 🔧 Troubleshooting

### Common Issues

**Camera not working?**
- Check if other apps are using the camera
- Try changing `CAMERA_INDEX` in `config.py` (0, 1, 2...)
- Restart the application

**Gestures not detected?**
- Ensure good lighting
- Move closer or farther from camera
- Press 'R' to reset calibration
- Make gestures more distinct

**App running slowly?**
- Close other heavy applications
- Lower the camera resolution in `config.py`
- Check your internet connection isn't being used by other apps

**Permission errors on macOS?**
- Go to System Preferences → Security & Privacy → Camera
- Enable camera access for Terminal/Python
- Do the same for Accessibility if needed

### Debug Mode

Enable detailed logging:
```python
# In config.py
LOG_LEVEL = 'DEBUG'
SHOW_DEBUG_INFO = True
```

## 🏗️ Project Structure

```
virtual-mouse/
├── .gitignore               # Git ignore rules
├── main.py                  # Main application (start here!)
├── virtual_mouse_modular.py # Alternative modular version
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
├── README.md                # You are here
├── gestures/
│   ├── __init__.py         # Package initialization
│   └── gesture_utils.py    # Gesture detection logic
├── screenshots/            # Auto-created for screenshots
└── tests/                  # Unit tests
```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python tests/test_fixes.py

# Verify bug fixes
python tests/verify_fixes.py

# Check import compatibility
python tests/check_imports.py
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** your changes
4. **Test** your changes: `python -m pytest`
5. **Commit**: `git commit -am 'Add new feature'`
6. **Push**: `git push origin feature-name`
7. **Submit** a Pull Request

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install development tools
pip install pylint black flake8 mypy

# Run code formatting (if tools installed)
black .
flake8 .
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | ~85% gesture recognition |
| **Latency** | ~100ms response time |
| **FPS** | 30 FPS video processing |
| **CPU Usage** | ~15-25% on modern hardware |

## 🔮 Roadmap

- [ ] **Multi-hand support** for advanced gestures
- [ ] **Gesture customization** interface
- [ ] **Voice command** integration
- [ ] **Mobile app** for remote control
- [ ] **AI-powered** gesture learning
- [ ] **Eye tracking** integration

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[MediaPipe](https://mediapipe.dev/)** - Google's ML framework for hand tracking
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[PyAutoGUI](https://pyautogui.readthedocs.io/)** - Cross-platform GUI automation

## ⭐ Support

If you find this project helpful, please consider:
- ⭐ **Starring** the repository
- 🐛 **Reporting bugs** via GitHub Issues
- � **Suggesting features** via GitHub Discussions
- 🤝 **Contributing** code or documentation

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/AkshayS734/virtual-mouse/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/AkshayS734/virtual-mouse/discussions)

---

**Made with ❤️ for accessible computing**
