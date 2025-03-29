''' 
This is a file to get the plant identification api data when querying a plant
Jana Armouti (jarmouti)

Using Pl@ntNet API 
'''

import requests
import json
import io
from pprint import pprint
from picamera2 import Picamera2
from PIL import Image
import matplotlib.pyplot as plt

API_KEY = "2b10KGTzAgqcb5baVQciCheRU"  # Set your API_KEY here
PROJECT = "all"  # try "weurope" or "canada"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

def identify_plant():
    picam2 = Picamera2()
    picam2.start()
    
    # capture image into memory
    image_stream = io.BytesIO()
    picam2.capture_file(image_stream, format="jpeg")
    image_stream.seek(0)
    '''
    image = Image.open(image_stream)
    plt.imshow(image)
    plt.axis('off')
    plt.show()'''

    files = [
        ('images', ('image.jpg', image_stream, 'image/jpeg'))
    ]

    response = requests.post(api_endpoint, files=files)

    json_result = response.json()

    pprint(response.status_code)
    pprint(json_result)

    if response.status_code == 200:
        best_match = json_result.get("bestMatch", "Unknown")
        common_names = json_result["results"][0]["species"].get("commonNames", [])
        print(f"Best match: {best_match}, Common names: {common_names}")

        return best_match, common_names

identify_plant()
