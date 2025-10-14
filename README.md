# UAV-Face Recognition System

## Overview

A complete face recognition system supporting both real-time streaming from Raspberry Pi and video file processing. The system detects and identifies faces using OpenCV and face_recognition libraries, with optimizations for edge computing devices.

**Demo Video:** [View System Demonstration](https://drive.google.com/file/d/13oGzSztC327xP8w98tWW2djFzsr0-9Z0/view?usp=sharing)

## System Architecture

The system consists of three main components:

1. **Raspberry Pi Streaming Server** (`stream.py`) - Captures and streams video from Pi camera
2. **Face Recognition Client** (`face_recog.py`) - Processes live stream with face recognition
3. **Video File Processor** (`face_recog_record.py`) - Batch processes uploaded video files

---

## Prerequisites

### Hardware Requirements

- Raspberry Pi 4 (4GB+ recommended)
- USB webcam or Pi Camera Module
- Computer for running face recognition client
- Network connection (same LAN for Pi and computer)

### Software Requirements

**Raspberry Pi:**

```
- Python 3.7+
- OpenCV
- Flask
```

**Client Computer:**

```
- Python 3.7+
- OpenCV
- face_recognition
- dlib
- numpy
- Flask
```

---

## Installation

### Part 1: Raspberry Pi Setup

#### 1.1 Install System Dependencies

Connect to your Raspberry Pi via SSH and run:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-opencv
```

#### 1.2 Install Python Packages

```bash
pip3 install flask opencv-python
```

Or use the requirements file:

```bash
pip3 install -r requirements_stream.txt
```

#### 1.3 Enable Camera (if using Pi Camera Module)

```bash
sudo raspi-config
```

Navigate to: `Interface Options` > `Camera` > `Enable`

Reboot the Pi:

```bash
sudo reboot
```

#### 1.4 Transfer Streaming Script

Copy `stream.py` to your Raspberry Pi:

```bash
# From your computer
scp stream.py pi@<RASPBERRY_PI_IP>:~/
```

#### 1.5 Find Raspberry Pi IP Address

On the Raspberry Pi, run:

```bash
hostname -I
```

Note the first IP address displayed (e.g., 192.168.1.100).

#### 1.6 Connect to Raspberry Pi via SSH

From your computer, connect to the Raspberry Pi:

```bash
ssh username@<RASPBERRY_PI_IP>
```

Example:

```bash
Enter your password when prompted. Default credentials:
- Username: `pi`
- Password: `raspberry` (change this after first login for security)


ssh pi@192.168.1.100
```

---

### Part 2: Client Computer Setup

#### 2.1 Install System Dependencies

**Windows:**

- Install Visual C++ Build Tools (required for dlib)
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Linux/macOS:**

```bash
# Ubuntu/Debian
sudo apt install build-essential cmake libopenblas-dev liblapack-dev

# macOS
brew install cmake
```

#### 2.2 Install Python Packages

```bash
pip install opencv-python face-recognition dlib numpy flask
```

Or use the requirements file for face recognition client:

```bash
pip install -r requirements_face_recog.txt
```

For video processing only:

```bash
pip install -r requirements_face_recog_record.txt
```

#### 2.3 Prepare Known Faces Database

1. Create an `images` folder in the project directory
2. Add photos of known individuals:
   - Use clear, front-facing photos
   - One face per image
   - Name each file after the person (e.g., `john_doe.jpg`, `jane_smith.png`)
   - Supported formats: JPG, JPEG, PNG

**Example structure:**

```
images/
├── john_doe.jpg
├── jane_smith.jpg
└── alice_johnson.png
```

---

## Usage

### Scenario 1: Real-Time Face Recognition from Raspberry Pi

This workflow streams video from Raspberry Pi and performs face recognition on your computer.

#### Step 1: Start Streaming Server on Raspberry Pi

Connect to your Raspberry Pi via SSH:

```bash
ssh pi@<RASPBERRY_PI_IP>
# Enter password when prompted
```

Then start the streaming server:

```bash
cd ~
python3 stream.py
```

Expected output:

```
============================================================
RASPBERRY PI VIDEO STREAMING SERVER
============================================================
Configuration:
  - Resolution: 320x240
  - FPS: 15
  - JPEG Quality: 50

Server starting on port 8080...
Access stream from your computer at:
  http://<RASPBERRY_PI_IP>:8080

To find Raspberry Pi IP address, run: hostname -I
============================================================
```

#### Step 2: Configure Face Recognition Client

On your computer, open `face_recog.py` and update the configuration:

```python
# Line 10-11: Update with your Raspberry Pi IP
cam_ip = "http://192.168.1.100:8080"  # Replace with your Pi's IP

# Line 14: Verify images folder path
images_path = "images"  # Folder containing known face images
```

#### Step 3: Run Face Recognition Client

```bash
python face_recog.py
```

Expected output:

```
============================================================
FACE RECOGNITION CLIENT
============================================================
Configuration:
  - Camera IP: http://192.168.1.100:8080
  - Images folder: images
============================================================
Loading known faces...
Loaded face: john_doe
Loaded face: jane_smith
Encoding complete: 2 faces loaded.

Starting Face Recognition Server...
Access the stream at: http://localhost:5000
============================================================
```

#### Step 4: Access Face Recognition Stream

Open a web browser and navigate to:

```
http://localhost:5000
```

**Visual Indicators:**

- Green boxes: Known/recognized faces
- Red boxes: Unknown faces
- Labels show names and FPS counter

---

### Scenario 2: Process Uploaded Video Files

This workflow processes pre-recorded videos and outputs annotated versions.

#### Step 1: Prepare Input Video

Place your video file in the `uploads` folder:

```
uploads/
└── face_recognition.mp4
```

Supported formats: MP4, AVI, MOV, MKV, FLV, WMV

#### Step 2: Configure Video Processor

Open `face_recog_record.py` and verify the configuration (lines 170-172):

```python
video_file = "uploads/face_recognition.mp4"  # Input video path
output_file = "output/processed_video.avi"   # Output video path
images_path = "images"                        # Known faces folder
```

**Adjust performance parameters** (lines 177-182):

```python
frame_resizing=0.50              # Scale: 0.5 = 50% size (faster)
process_every_n_frames=10        # Process every 10th frame
center_region_percent=0.5        # Focus on center 50% of frame
```

#### Step 3: Run Video Processor

```bash
python face_recog_record.py
```

Expected output:

```
Starting video processing...
Input video: uploads/face_recognition.mp4
Output video: output/processed_video.avi
Known faces folder: images
------------------------------------------------------------
Loading known faces...
Loaded face: john_doe
Loaded face: jane_smith
Encoding complete: 2 faces loaded.

Video Properties - FPS: 30, Resolution: 1920x1080, Total Frames: 3600
Processing video...
Progress: 25.0% (900/3600) ETA: 45s
Progress: 50.0% (1800/3600) ETA: 22s
Progress: 75.0% (2700/3600) ETA: 11s
Processing complete! Total time: 60s (1.0 minutes)
Video saved successfully to: output/processed_video.avi
Output file size: 234.56 MB
```

#### Step 4: View Processed Video

The annotated video will be saved in the `output` folder. Open with any media player.

---

## Configuration Options

### Stream Server Settings (`stream.py`)

```python
FRAME_WIDTH = 320      # Video width (lower = faster)
FRAME_HEIGHT = 240     # Video height (lower = faster)
FPS = 15               # Frames per second
JPEG_QUALITY = 50      # Compression quality (1-100)
```

**Recommendations:**

- Low bandwidth: 320x240, FPS=10, Quality=40
- Balanced: 320x240, FPS=15, Quality=50
- High quality: 640x480, FPS=20, Quality=70

### Face Recognition Settings (`face_recog.py`)

```python
frame_resizing = 0.25           # Processing scale (0.25 = 25% size)
process_every_n_frames = 2      # Process every 2nd frame
```

### Video Processing Settings (`face_recog_record.py`)

```python
frame_resizing = 0.50           # Scale factor for processing
process_every_n_frames = 10     # Frame skip interval
center_region_percent = 0.5     # Detection focus area
```

**Performance vs Accuracy Trade-offs:**

| Setting                | Fast | Balanced | Accurate |
| ---------------------- | ---- | -------- | -------- |
| frame_resizing         | 0.25 | 0.50     | 1.0      |
| process_every_n_frames | 15   | 10       | 2        |
| center_region_percent  | 0.3  | 0.5      | 1.0      |

---

## Troubleshooting

### Issue: Raspberry Pi stream not accessible

**Solution:**

1. Verify Pi is on same network: `ping <RASPBERRY_PI_IP>`
2. Check firewall settings on Pi
3. Ensure stream.py is running without errors
4. Test stream URL in browser: `http://<RASPBERRY_PI_IP>:8080`

### Issue: No faces detected in images folder

**Solution:**

1. Verify image files are in correct format (JPG/PNG)
2. Ensure faces are clearly visible and front-facing
3. Check console output for encoding errors
4. Test with high-quality reference photos

### Issue: Face recognition too slow

**Solution:**

1. Reduce `frame_resizing` value (e.g., 0.25)
2. Increase `process_every_n_frames` (e.g., 5-10)
3. Lower stream resolution on Raspberry Pi
4. Use `model='hog'` instead of `model='cnn'` in detection

### Issue: Low recognition accuracy

**Solution:**

1. Increase `frame_resizing` value (closer to 1.0)
2. Decrease `process_every_n_frames` (process more frames)
3. Add multiple photos per person to images folder
4. Ensure good lighting in video/stream
5. Use `model='cnn'` for better accuracy (slower)

### Issue: Video file processing fails

**Solution:**

1. Verify video codec is supported (try converting to MP4)
2. Check video file is not corrupted
3. Ensure sufficient disk space for output
4. Try reducing output quality or resolution

---

## Technical Details

### Face Detection Algorithm

The system uses a hybrid approach:

1. **Haar Cascade** for initial fast detection (face_recog_record.py)
2. **HOG/CNN models** for accurate localization (configurable)
3. **face_recognition** library for encoding and matching

### Recognition Process

1. Load known face encodings from images folder
2. Detect faces in frame using selected model
3. Generate 128-dimensional encoding for each detected face
4. Compare with known encodings using Euclidean distance
5. Match if distance < 0.6 threshold

### Performance Optimizations

- Frame skipping for reduced processing load
- Resolution scaling for faster encoding
- Center region focus for drone/surveillance footage
- Multi-threaded streaming for smooth playback
- JPEG compression for bandwidth efficiency

---

## File Structure

```
Face_Recognition/
├── stream.py                 # Pi streaming server
├── face_recog.py            # Real-time recognition client
├── face_recog_record.py     # Video file processor
├── raspberry_pi_face_recognition.py  # Standalone Pi script
├── pi_setup.sh              # Pi installation script
├── requirements_stream.txt          # Dependencies for stream.py
├── requirements_face_recog.txt      # Dependencies for face_recog.py
├── requirements_face_recog_record.txt  # Dependencies for face_recog_record.py
├── README.md                # This documentation
├── images/                  # Known faces database
│   ├── person1.jpg
│   └── person2.jpg
├── uploads/                 # Input videos
│   └── face_recognition.mp4
└── output/                  # Processed videos
    └── processed_video.avi
```

---

## Advanced Usage

### Using Pi Camera Module Instead of USB Camera

Edit `stream.py` line 13:

```python
# Replace:
camera = cv2.VideoCapture(0)

# With:
camera = cv2.VideoCapture('libcamerasrc ! videoconvert ! videoscale ! video/x-raw,width=320,height=240,framerate=15/1 ! appsink', cv2.CAP_GSTREAMER)
```

### Running as Background Service on Pi

Create systemd service file `/etc/systemd/system/face-stream.service`:

```ini
[Unit]
Description=Face Recognition Stream Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/stream.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable face-stream
sudo systemctl start face-stream
```

---

## Performance Benchmarks

**Raspberry Pi 4 (4GB):**

- Stream: 15 FPS @ 320x240
- Face detection: 8-12 FPS
- Network latency: <100ms (LAN)

**Client Computer (i5-8250U):**

- Processing: 20-25 FPS @ 50% scaling
- Recognition: 15-20 FPS with 3 known faces
- Video processing: 2x realtime speed

---

## Security Considerations

1. **Network Security**: Use VPN for remote access, avoid exposing Pi directly to internet
2. **Data Privacy**: Store face encodings securely, comply with local privacy laws
3. **Authentication**: Add password protection to web interfaces in production
4. **HTTPS**: Use SSL certificates for encrypted streaming in production environments

---

## License

This project is for educational purposes. Use responsibly and respect privacy laws in your jurisdiction.

---

## Support

For issues or questions:

1. Check Troubleshooting section above
2. Verify all configuration values are correct
3. Review console output for error messages
4. Ensure all dependencies are properly installed

---

## Version History

- v1.0.0 - Initial release with streaming and video processing capabilities

A simple, beginner-friendly face recognition system optimized for Raspberry Pi 4. This project detects and recognizes faces using OpenCV and lightweight algorithms perfect for edge computing.

## 🚀 Features

- **Lightweight**: Uses Haar Cascades for fast face detection
- **Pi-Optimized**: Designed specifically for Raspberry Pi 4 performance
- **Real-time**: Live camera feed with face detection and recognition
- **Simple Database**: Easy-to-use face database with pickle storage
- **Beginner-friendly**: Clear code with lots of comments and explanations

## 📦 What's Included

1. **tfile.ipynb** - Jupyter notebook with step-by-step implementation
2. **raspberry_pi_face_recognition.py** - Complete standalone Python script
3. **pi_setup.sh** - Automated setup script for Raspberry Pi
4. **Sample images** - Test images in the `images/` folder

## 🔧 Installation

### On Your Computer (Testing)

```bash
pip install opencv-python numpy matplotlib pillow
```

### On Raspberry Pi 4

```bash
# Method 1: Automated setup
chmod +x pi_setup.sh
./pi_setup.sh

# Method 2: Manual setup
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-opencv python3-numpy
pip3 install opencv-python numpy
```

## 🎮 Usage

### Testing on Computer

1. Open `tfile.ipynb` in Jupyter Notebook
2. Run each cell step by step
3. Test with the provided sample images

### Running on Raspberry Pi

```bash
python3 raspberry_pi_face_recognition.py
```

### Controls

- **Q** - Quit the application
- **S** - Save current face (you'll be prompted for a name)
- **R** - Recognize faces in current frame
- **ESC** - Close camera window

## 📊 Performance on Raspberry Pi 4

- **Resolution**: 320x240 (optimized for speed)
- **FPS**: ~10-15 fps with face detection
- **Memory**: ~150MB RAM usage
- **CPU**: ~30-40% usage on Pi 4

## 🔧 Optimization Tips

1. **Improve Performance**:

   - Use a fast SD card (Class 10+)
   - Enable GPU memory split: `sudo raspi-config` → Advanced → Memory Split → 128
   - Close unnecessary applications
   - Use good lighting conditions

2. **Better Accuracy**:
   - Take multiple photos per person
   - Ensure good lighting when adding faces
   - Use frontal face photos
   - Consider upgrading to `face_recognition` library for better accuracy

## 🆙 Upgrades for Production

### Advanced Face Recognition

```bash
# Install face_recognition for better accuracy (requires more resources)
sudo apt install cmake libopenblas-dev liblapack-dev
pip3 install face_recognition dlib
```

### Camera Improvements

```bash
# For Pi Camera module
sudo raspi-config  # Enable camera interface
pip3 install picamera
```

## 🐛 Troubleshooting

### Camera Issues

- Make sure camera is connected and detected: `lsusb`
- For Pi camera: enable in `raspi-config`
- Check permissions: add user to video group

### Performance Issues

- Reduce frame resolution in the code
- Process every N-th frame (already implemented)
- Close other applications
- Check CPU temperature: `vcgencmd measure_temp`

### Recognition Issues

- Ensure good lighting
- Add multiple photos per person
- Check if faces are properly detected first
- Consider using the advanced face_recognition library

## 📚 Learning Path

1. **Start Here**: Run the Jupyter notebook (`tfile.ipynb`)
2. **Understand**: Read through each cell and understand the concepts
3. **Test**: Try the system with your own photos
4. **Deploy**: Copy to Raspberry Pi and test with camera
5. **Improve**: Experiment with different parameters and optimizations

## 🎯 Next Steps for Your Pi Project

1. **Add Database**: Store faces in a proper database (SQLite)
2. **Web Interface**: Create a web dashboard for management
3. **Alerts**: Send notifications when unknown faces are detected
4. **Time Tracking**: Build an attendance system
5. **Mobile App**: Create a mobile interface

## 📝 Technical Details

- **Face Detection**: OpenCV Haar Cascades
- **Feature Extraction**: Histogram comparison (basic) or face_recognition (advanced)
- **Database**: Pickle files (can be upgraded to SQLite)
- **Camera**: OpenCV VideoCapture
- **Platform**: Optimized for Raspberry Pi 4 (4GB+ recommended)

## 🤝 Contributing

This is a beginner-friendly project! Feel free to:

- Add new features
- Improve performance
- Fix bugs
- Enhance documentation

## ⚠️ Notes

- This is a basic implementation for learning purposes
- For production security systems, use advanced face recognition libraries
- Always respect privacy and get consent before capturing faces
- Test thoroughly before deploying in real-world scenarios

## 📄 License

This project is for educational purposes. Use responsibly and respect privacy laws in your area.

---

**Happy coding on your Raspberry Pi! 🥧🤖**
