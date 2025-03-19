''' 
This is a file to get the plant api data when querying a plant
Zara Mansoor (zmansoor)

Using Perenual 

'''
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://perenual.com/api/v2"
PERENUAL_API_TOKEN = os.getenv("PERENUAL_API_KEY")

def api_call(call_name, query):
  if query:
    url = f"{BASE_URL}/{call_name}?key={PERENUAL_API_TOKEN}&{query}"
  else:
    url = f"{BASE_URL}/{call_name}?key={PERENUAL_API_TOKEN}"

  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return data
  else:
    print(f"Error: {response.status_code}, {response.text}")
    return []

def get_plants():
  call_name = "species-list"
  plants = api_call(call_name, None)["data"]

  for plant in plants[:5]:
    print(plant)
 
def search_plant(search_query):
  call_name = "species-list"
  query = f"q={search_query}"
  plants = api_call(call_name, query)["data"]

  for plant in plants:
    print(f"Plant id: {plant['id']} \t common name: {plant['common_name']} \t other name: {plant['other_name']} \t scientific name: {plant['scientific_name']} \t image: {plant['default_image']}")

def retrieve_plant(id):
  call_name = f"species/details/{id}"
  plant = api_call(call_name, None)

  print(plant)
  # print(f"Plant id: {plant['id']} \t common name: {plant['common_name']} \t other name: {plant['other_name']} \t scientific name: {plant['scientific_name']} \t image: {plant['default_image']}")


def main():
  # get_plants()
  plant_name = input("Please enter a plant name: ")
  search_plant(plant_name)
  plant_id = input("Please enter a plant id: ")
  try:
    plant_id = int(plant_id)
    retrieve_plant(plant_id)
  except ValueError:
    print("Invalid input! Please enter a valid plant ID.")
    
    
if __name__ == "__main__":
  main()
    
    