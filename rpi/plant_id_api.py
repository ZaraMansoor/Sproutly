''' 
This is a file to get the plant identification api data when querying a plant
Jana Armouti (jarmouti)

Using Pl@ntNet API 
'''

import requests
import json
from pprint import pprint
from picamera2 import Picamera2

API_KEY = "2b10KGTzAgqcb5baVQciCheRU"  # Set you API_KEY here
PROJECT = "all" # try "weurope" or "canada"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

def identify_plant():
  picam2 = Picamera2()
  picam2.start_and_capture_file("data/test.jpg")
  image_path_1 = "data/test.jpg"
  image_data_1 = open(image_path_1, 'rb')

  files = [
      ('images', (image_path_1, image_data_1))
  ]

  req = requests.Request('POST', url=api_endpoint, files=files, data={})
  prepared = req.prepare()

  s = requests.Session()
  response = s.send(prepared)
  json_result = json.loads(response.text)

  pprint(response.status_code)
  pprint(json_result)

  if (response.status_code == 200):
    best_match = json_result["bestMatch"]
    common_names = json_result["results"][0]["species"]["commonNames"]
    print(f"best match: {best_match}, common names: {common_names}")

    return best_match, common_names