''' 
This is a file to get the plant identification api data when querying a plant
Jana Armouti (jarmouti)

Using Pl@ntNet API 
'''
from picamera2 import Picamera2
from PIL import Image
import numpy as np
from libcamera import Transform
import io
import requests
API_KEY = "2b10KGTzAgqcb5baVQciCheRU"  # Set your API_KEY here
PROJECT = "all"  # try "weurope" or "canada"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

def identify_plant(files):
    response = requests.post(api_endpoint, files=files)
    json_result = response.json()
    if response.status_code == 200:
        best_match = json_result.get("bestMatch", "Unknown")
        common_names = json_result["results"][0]["species"].get("commonNames", [])
        return best_match, common_names

if __name__ == "__main__":
    # adjustable settings
    RESOLUTION = (3280, 2464)
    FRAME_RATE = 30
    JPEG_QUALITY = 100 # (1 - 100)

    # define daytime (bright light) settings
    DAY_SETTINGS = {
        "AeEnable": True,          # Auto exposure enabled
        "FrameRate": 30,           # Higher frame rate
        "AnalogueGain": 1.0,       # Low analog gain
        "Sharpness": 2.0,
    }

    # define nighttime (low light) settings
    NIGHT_SETTINGS = {
        "AeEnable": False,         # Disable auto exposure
        "FrameRate": 15,           # Lower frame rate for better low-light performance
        "ExposureTime": 30000,     # Longer exposure time (30ms)
        "AnalogueGain": 2.0,       # Increase analog gain
        "Sharpness": 2.0,
    }

    LIGHT_THRESHOLD = 100
    BRIGHTNESS_SAMPLES = 10

    # initialize PiCamera2 for video streaming
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={'size': RESOLUTION},
        transform=Transform(hflip=1, vflip=1)
    )

    picam2.configure(config)
    picam2.set_controls({"FrameRate": FRAME_RATE})


    picam2.start()
    image_stream = io.BytesIO()
    picam2.capture_file(image_stream, format="jpeg")
    image_stream.seek(0)
    picam2.stop()

    files = [
      ('images', ('image.jpg', image_stream, 'image/jpeg'))
    ]
    best_match, common_names = identify_plant(files)

    print(f"best_match: {best_match}")
    print(f"common_names: {common_names}")