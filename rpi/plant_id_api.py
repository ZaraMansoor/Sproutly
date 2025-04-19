''' 
This is a file to get the plant identification api data when querying a plant
Jana Armouti (jarmouti)

Using Pl@ntNet API 
'''

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
    identify_plant()
