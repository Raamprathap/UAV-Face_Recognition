from flask import Flask, Response
import cv2
import threading
from collections import deque

app = Flask(__name__)

# CONFIGURATION FOR RASPBERRY PI
# Adjust these settings based on your camera and network requirements
FRAME_WIDTH = 320   # Lower resolution for better performance on Pi
FRAME_HEIGHT = 240
FPS = 15            # Frames per second
JPEG_QUALITY = 50   # JPEG compression quality (1-100, lower = smaller size)

# Initialize camera
# Use 0 for USB camera, or for Pi Camera use:
# camera = cv2.VideoCapture('libcamerasrc ! videoconvert ! videoscale ! video/x-raw,width=320,height=240,framerate=15/1 ! appsink', cv2.CAP_GSTREAMER)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
camera.set(cv2.CAP_PROP_FPS, FPS)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

latest_frame = None
frame_lock = threading.Lock()

def capture_frames():
    """Continuously capture frames in a separate thread"""
    global latest_frame
    while True:
        success, frame = camera.read()
        if success:
            with frame_lock:
                latest_frame = frame

capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

def gen_frames():
    """Generate frames with optimized encoding"""
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        
        # Encode frame with compression for efficient streaming
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + 
                   buffer.tobytes() + b'\r\n')

@app.route('/')
def video():
    return Response(gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("RASPBERRY PI VIDEO STREAMING SERVER")
    print("="*60)
    print(f"Configuration:")
    print(f"  - Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  - FPS: {FPS}")
    print(f"  - JPEG Quality: {JPEG_QUALITY}")
    print(f"\nServer starting on port 8080...")
    print(f"Access stream from your computer at:")
    print(f"  http://<RASPBERRY_PI_IP>:8080")
    print(f"\nTo find Raspberry Pi IP address, run: hostname -I")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
