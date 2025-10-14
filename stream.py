stream

from flask import Flask, Response
import cv2
import threading
from collections import deque

app = Flask(_name_)

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FPS = 15

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
        
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + 
                   buffer.tobytes() + b'\r\n')

@app.route('/video')
def video():
    return Response(gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
