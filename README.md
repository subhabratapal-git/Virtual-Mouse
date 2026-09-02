# 🖱️ Virtual Mouse Using Hand Gesture

A real-time **AI-powered Virtual Mouse** that allows users to control the computer mouse using **hand gestures captured through a webcam**.

The project uses **MediaPipe Hand Tracking** to detect hand landmarks and **OpenCV** for real-time video processing. Mouse actions such as cursor movement, left click, double click, right click, drag, and scrolling are performed using **PyAutoGUI**.

> **Project: Virtual Mouse,**
> **Author: Subhabrata Pal,**
> **Language: Python**

---

## ✨ Features

* ☝️ **Index Finger Movement** → Move the mouse cursor
* 🤏 **Index Finger + Thumb Pinch** → Left Click
* 🤏 **Index Finger + Thumb Hold for 1 second** → Double Click
* 🤏 **Middle Finger + Thumb Pinch** → Right Click
* 🤏 **Middle Finger + Thumb Hold for 1 second** → Drag
* ✊ **Closed Fist** → Scroll
* 🎯 **One Euro Filter** → Smooth and stable cursor movement
* 🔄 **Hand Detection Recovery** → Automatically resets states when the hand is lost
* 🛡️ **Pinch Hysteresis** → Separate enter/exit thresholds reduce accidental clicks
* 📊 **Real-Time Gesture Status UI**
* 🎥 **Live Webcam Hand Tracking**
* 🖥️ **Screen Boundary Protection**

---

## 🛠️ Technologies Used

| Technology    | Purpose                            |
| ------------- | ---------------------------------- |
| **Python**    | Core programming language          |
| **OpenCV**    | Webcam access and image processing |
| **MediaPipe** | Hand landmark detection            |
| **PyAutoGUI** | Mouse and scrolling control        |
| **Math**      | Distance and movement calculations |
| **Time**      | Gesture hold-time detection        |

---

## 📁 Project Structure

```text
Virtual-Mouse/
│
├── main.py
├── README.md

```

---

## ⚙️ How It Works

The system captures video from the webcam and processes each frame using OpenCV.

MediaPipe detects the user's hand and identifies **21 hand landmarks**.

The project then analyzes the positions of different fingertips to determine the user's gesture.

### Basic Flow

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Detection
   ↓
21 Hand Landmarks
   ↓
Gesture Recognition
   ↓
PyAutoGUI
   ↓
Mouse Action
```

---

## 🖐️ Gesture Controls

| Hand Gesture              | Action       |
| ------------------------- | ------------ |
| ☝️ Index Finger Up        | Move Cursor  |
| 🤏 Index + Thumb          | Left Click   |
| 🤏 Index + Thumb Hold 1s  | Double Click |
| 🤏 Middle + Thumb         | Right Click  |
| 🤏 Middle + Thumb Hold 1s | Drag         |
| ✊ All Fingers Closed      | Scroll       |

---

## 🎯 Cursor Movement

The cursor movement is based on the position of the **index fingertip**.

The detected coordinates are filtered using a custom **One Euro Filter** to reduce small hand movements and camera noise.

The project also uses:

* **Sensitivity control**
* **Deadzone**
* **Cursor boundary limits**
* **Previous-position tracking**

These techniques help make cursor movement smoother and more stable.

---

## 🤏 Pinch Detection

Pinch gestures are detected by calculating the distance between the thumb tip and the selected fingertip.

For example:

```text
Index Tip
    ●
     \
      ● Thumb Tip
```

If the distance becomes smaller than the pinch threshold, the gesture is considered active.

The project uses two thresholds:

```python
PINCH_ENTER = 0.032
PINCH_EXIT = 0.050
```

Using separate enter and exit thresholds helps prevent gesture flickering caused by small movements.

---

## 🎯 One Euro Filter

A custom **One Euro Filter** is implemented to smooth the cursor movement.

Instead of directly moving the cursor according to every detected landmark position, the filter reduces unwanted noise while still allowing faster movements to remain responsive.

This helps solve problems such as:

* Cursor jitter
* Small unwanted movements
* Camera tracking noise
* Unstable hand landmarks

---

## ✋ Hand Loss Protection

If the camera temporarily loses the hand, the program waits for a small number of frames before resetting the mouse state.

```python
HAND_LOST_GRACE_FRAMES = 5
```

This prevents temporary detection failures from immediately interrupting the interaction.

If the hand remains undetected:

* Cursor tracking is reset
* Pinch states are cleared
* Dragging is released
* Scroll state is reset
* Filters are reset

This provides safer mouse behavior.

---

## 📊 Real-Time Interface

The webcam window includes a custom interface showing:

* Current gesture status
* Hand detection status
* Camera status
* Smoothing status
* Gesture instructions
* Hold progress

Example status messages:

```text
INDEX -> MOVE
LEFT CLICK
DOUBLE CLICK READY
RIGHT CLICK
DRAGGING
SCROLL
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/subhabratapal-git/Virtual-Mouse.git
```

### 2. Open the Project

```bash
cd Virtual-Mouse
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, install the required packages manually:

```bash
pip install opencv-python mediapipe pyautogui
```

---

## ▶️ Run the Project

Start the application using:

```bash
python main.py
```

A webcam window will open automatically.

Place your hand in front of the camera and use the supported gestures to control the mouse.

### Exit

Press:

```text
Q
```

to close the application.

---

## ⚙️ Configuration

The main interaction parameters can be adjusted in `main.py`.

### Cursor Sensitivity

```python
SENSITIVITY = 2.2
```

Increase the value for faster cursor movement.

Decrease it for slower and more precise movement.

### Deadzone

```python
DEADZONE = 0.0015
```

The deadzone prevents very small hand movements from moving the cursor.

### Pinch Threshold

```python
PINCH_ENTER = 0.032
PINCH_EXIT = 0.050
```

These values control how close the thumb and fingertip need to be for a pinch gesture.

### Hold Duration

```python
HOLD_TIME = 1.0
```

The gesture must be held for approximately one second to trigger the hold-based action.

---

## 📦 requirements.txt

Create a file named `requirements.txt`:

```text
opencv-python
mediapipe
pyautogui
```

Then install everything with:

```bash
pip install -r requirements.txt
```

---

## 💡 Use Cases

This project demonstrates how computer vision and hand tracking can be used to create a touchless human-computer interaction system.

Possible use cases include:

* 🖥️ Touchless computer control
* ♿ Accessibility applications
* 🎓 Computer vision learning
* 🤖 Human-computer interaction research
* 🧪 Gesture recognition experiments
* 🎮 Experimental gesture-based interfaces

---

## 🔮 Future Improvements

The project can be further improved by adding:

*  Multi-hand support
*  Keyboard control using gestures
*  Gesture-based application switching
*  Machine-learning-based gesture classification

---

## ⚠️ Limitations

The performance of the system depends on:

* Webcam quality
* Lighting conditions
* Hand visibility
* Camera position
* Hand distance from the camera
* MediaPipe tracking accuracy

For best results, use the system in a well-lit environment with your hand clearly visible to the camera.

---

## 🧠 What I Learned

Through this project, I explored practical applications of:

* Computer Vision
* Hand Landmark Detection
* Real-Time Video Processing
* Gesture Recognition
* Coordinate Mapping
* Signal Filtering
* Mouse Automation
* State Management
* Human-Computer Interaction

The project also helped me understand how raw computer vision data can be converted into meaningful user interactions.

---

## 👨‍💻 Author

### Subhabrata Pal

Computer Science Engineering Student

Kolkata, West Bengal, India

Interested in:

* Python
* Data Structures & Algorithms
* Machine Learning
* Computer Vision
* Software Development

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is created for **educational and experimental purposes**.

You are free to modify and improve the project for learning and personal use.
