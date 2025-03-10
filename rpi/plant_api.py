''' 
This is a file to get the plant api data when querying a plant
Zara Mansoor (zmansoor)

'''
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://trefle.io/api/v1"
TREFLE_API_TOKEN = os.getenv("TREFLE_API_KEY")

def get_plants():
  url = f"{BASE_URL}/plants?token={TREFLE_API_TOKEN}"
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return data["data"]
  else:
    print(f"Error: {response.status_code}, {response.text}")
    return None
  
def main():
  plants = get_plants()
  
  for plant in plants[:5]:
    print(plant)
    
    
if __name__ == "__main__":
  main()
    
    