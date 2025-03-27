'''
File to live stream onto a simple web page through Raspberry Pi.
Uses PiCamera2 to capture frames and serve them as an MJPEG stream.

Original Documentation: https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
Modified to work on Raspberry Pi 5 with adjustable resolution, frame rate, and quality.
'''

import io
import logging
import socketserver
from http import server
from threading import Condition
from picamera2 import Picamera2
from PIL import Image
import numpy as np

# adjustable settings
RESOLUTION = (3280, 2464)
FRAME_RATE = 30
JPEG_QUALITY = 90 # (1 - 100)

# define daytime (bright light) settings
DAY_SETTINGS = {
    "FrameRate": 30,           # higher frame rate
    "ExposureTime": 10000,     # short exposure time (10ms)
    "ISO": 100,                # low ISO to avoid noise in bright light
    "AnalogueGain": 1.0,       # low analog gain
    "AwbMode": "auto",         # automatic white balance
}

# define nighttime (low light) settings
NIGHT_SETTINGS = {
    "FrameRate": 15,           # lower frame rate for better low-light performance
    "ExposureTime": 30000,     # longer exposure time (30ms)
    "ISO": 800,                # higher ISO to capture more light
    "AnalogueGain": 2.0,       # increase analog gain to brighten image in low light
    "AwbMode": "incandescent", # adjust white balance for artificial light (or "fluorescent")
}

LIGHT_THRESHOLD = 100

# HTML page for the web interface
PAGE='''\
<html>
<head>
<title>Sproutly Streaming</title>
</head>
<body>
<h1>Sproutly Streaming</h1>
<img src='stream.mjpg' width='640' height='480' />
</body>
</html>
'''

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update_frame(self, new_frame):
        # New frame, copy the existing buffer's content and notify all
        # clients it's available
        with self.condition:
            self.frame = new_frame
            self.condition.notify_all()

# handles HTTP requests for the web stream.
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

# multi-threaded HTTP server to handle multiple clients.
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# initialize PiCamera2 for video streaming
picam2 = Picamera2()
config = picam2.create_video_configuration(main={'size': RESOLUTION})
picam2.configure(config)
picam2.set_controls({"FrameRate": FRAME_RATE})
picam2.start()

# create an instance to store streaming frame
output = StreamingOutput()

# adjust camera settings based on light levels 
# (to support day and night conditions)
def adjust_camera_settings():
    # capture and image and estimate the light level
    frame = picam2.capture_array('main')
    brightness = np.mean(frame) 
    a = 'day' if (brightness > LIGHT_THRESHOLD) else 'night'
    print(brightness, ())

    settings = DAY_SETTINGS if (brightness > LIGHT_THRESHOLD) else NIGHT_SETTINGS
    picam2.set_controls(settings)

# continuously capture JPEG frames and update the streaming output
def capture_frames():
    while True:
        adjust_camera_settings()
        frame = picam2.capture_array('main')
        img = Image.fromarray(frame).convert('RGB')
        with io.BytesIO() as buf:
            img.save(buf, format='JPEG', quality=JPEG_QUALITY)
            output.update_frame(buf.getvalue())

# start capturing frames in a background thread
import threading
threading.Thread(target=capture_frames, daemon=True).start()

# start HTTP server
try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    print('Starting server on port 8000...')
    server.serve_forever()
finally:
    picam2.stop()
