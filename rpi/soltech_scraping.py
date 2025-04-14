''' 
This is a file to get the plant data by webscraping gardenia.net
Zara Mansoor (zmansoor)

'''
import requests
from bs4 import BeautifulSoup
import re

def main():
  base_url = f"https://soltech.com"
  url = f"https://soltech.com/collections/plant-guide"
  print(url)

  response = requests.get(url)
  
  if response.status_code != 200:
    print(response.status_code, " Failed to retrieve the page.")
    return
  
  soup = BeautifulSoup(response.content, "html.parser")
  plants = soup.find_all("div", class_="one-fourth") 

  plant_data = []
  for plant in plants:
    # get plant name
    namelink_tag = plant.find("a", class_="product-thumbnail__title")
    if namelink_tag:
      name = namelink_tag.text.strip()
      href = base_url + namelink_tag.get("href")

    # get img url
    img_tag = plant.find("img", class_="lazyload")
    img_url = "https:" + img_tag["data-src"] if img_tag and "data-src" in img_tag.attrs else "No Image"

    plant_data.append((name, img_url, href))

  ph_map = {
    "African Milk Tree": [6.0, 8.0],
    "African Violet": [6.0, 7.0],
    "Alocasia Polly": [5.5, 6.5],
    "Aloe Plant": [5.5, 7.0],
    "Amaryllis": [5.5, 6.5],
    "Anthurium": [5.0, 6.0],
    "Areca Palm": [6.0, 6.5],
    "Basil": [5.5, 6.5],
    "Bird of Paradise": [6.0, 6.5],
    "Birds Nest Fern": [5.0, 5.5],
    "Boston Fern": [5.5, 6.5],
    "Burro's Tail": [6.0, 7.0],
    "Caladium": [6.0, 7.5],
    "Calamondin": [5.5, 7.0],
    "Calathea Medallion": [6.0, 6.5],
    "Calathea Orbifolia": [6.5, 7.0],
    "Calathea Rattlesnake": [6.0, 7.0],
    "Cast Iron Plant": [5.5, 7.0],
    "Chinese Evergreen": [5.5, 6.5],
    "Chinese Money Plant": [6.0, 7.0],
    "Chives": [6.0, 7.0],
    "Christmas Cactus": [5.0, 6.5],
    "Cilantro": [6.0, 7.0],
    "Coral Cactus": [6.0, 7.0],
    "Croton": [5.0, 6.0],
    "Desert Rose": [6.0, 7.0],
    "Dieffenbachia": [5.0, 6.0],
    "Dill": [5.5, 6.5],
    "Dragon Tree": [6.0, 7.0],
    "Elephant Ear": [5.5, 7.0],
    "English Ivy": [6.5, 7.5],
    "Ficus Audrey": [6.0, 7.0],
    "Fiddle Leaf Fig": [6.0, 7.0],
    "Fishbone Cactus": [6.0, 7.5],
    "Friendship Plant": [6.0, 6.5],
    "Golden Pothos": [6.0, 6.5],
    "Heartleaf Philodendron": [5.5, 6.5],
    "Hindu Rope Plant": [6.0, 7.0],
    "Jade Plant": [6.0, 7.0],
    "Lavender": [6.5, 7.5],
    "Maranta": [5.5, 6.0],
    "Meyer Lemon Tree": [5.5, 6.5],
    "Mini Monstera": [5.5, 7.0],
    "Money Tree": [6.0, 7.5],
    "Monstera Adansonii": [5.5, 7.0],
    "Monstera deliciosa": [5.5, 7.0],
    "Moth Orchid": [5.5, 6.5],
    "Nerve Plant": [5.5, 7.0],
    "Oregano": [6.0, 8.0],
    "Oxalis": [6.0, 8.0],
  }

  for i in range(len(plant_data)):
    name, img, href = plant_data[i]
    print(f"{i}: {name}, Image URL: {img}, Link: {href}")
    
  plant_id = input("Please enter plant index number: ")

  name, img, url = plant_data[int(plant_id)]
  print(url)

  response = requests.get(url)
  
  if response.status_code != 200:
    print(response.status_code, " Failed to retrieve the page.")
    return
  
  soup = BeautifulSoup(response.content, "html.parser")
  # scientific_name, light, watering ?, temp, humidity
  # still need pH and consistent watering system
  plant_info = dict()

  plant_info["name"] = name

  scientific_name = "n/a"
  scientific_name_tag = soup.find("strong", string=lambda text: text and "SCENTIFIC NAME" in text)
  if scientific_name_tag:
    # Get the parent <p> tag and then find the second <strong> inside it
    parent_span_sci = scientific_name_tag.find_parent("p")
    if parent_span_sci:
      scientific_name = parent_span_sci.get_text(strip=True).replace("SCENTIFIC NAME:", "").strip()

  plant_info["scientific_name"] = scientific_name

  # map of light_description: [light_intensity]
  light_map = {
    'Full Sun (Bright Direct Light) & High Light (Bright Indirect Light)': 4,
    'High Light (Bright Indirect Light)': 3, 
    'High Light (Bright Indirect Light); Low Light Tolerant': 3,
    'Medium Light (Medium Indirect Light) to High Light (Bright Indirect Light)': 2,
    'Medium Light (Medium Indirect Light) to High Light (Bright Indirect Light); Low Light Tolerant': 1
  }

  light = "n/a"
  light_tag = soup.find("strong", string=lambda text: text and "Light Requirement" in text)
  if light_tag:
    parent_p_light = light_tag.find_parent("p")
    if parent_p_light:
      strong_tags = parent_p_light.find_all("strong")
      if len(strong_tags) > 1:
        light = strong_tags[1].text.strip()

  plant_info["light_description"] = light
  plant_info["light_intensity"] = light_map[light]

  water = "n/a"
  water_tag = soup.find("strong", string=lambda text: text and "Quick Tip" in text)
  if water_tag:
    parent_p_water = water_tag.find_parent("p")
    if parent_p_water:
      strong_tags = parent_p_water.find_all("strong")
      if len(strong_tags) > 1:
        water = strong_tags[1].text.strip()

  plant_info["water"] = water

  temp, temp_min_F, temp_max_F = "n/a"
  temp_tag = soup.find("strong", string=lambda text: text and "Preferred Temperature" in text)
  if temp_tag:
    parent_p_temp = temp_tag.find_parent("p")
    if parent_p_temp:
      strong_tags = parent_p_temp.find_all("strong")
      if len(strong_tags) > 1:
        temp = strong_tags[1].text.strip()
        temp_range = temp.split("-")
        
        if len(temp_range) == 2:
          temp_min_F = re.sub(r"[^\d]", "", temp_range[0].strip())
          temp_max_F = re.sub(r"[^\d]", "", temp_range[1].strip())

  plant_info["temp_min_F"] = temp_min_F
  plant_info["temp_max_F"] = temp_max_F

  humidity_min = "n/a"
  humidity_max = "n/a"

  humidity_tag = soup.find("strong", string=lambda text: text and "Preferred Humidity" in text)
  if humidity_tag:
    parent_p_humidity = humidity_tag.find_parent("p")
    if parent_p_humidity:
      strong_tags = parent_p_humidity.find_all("strong")
      if len(strong_tags) > 1:
        humidity = strong_tags[1].text.strip()

        # extract min and max humidity (e.g., "40 - 50%")
        humidity_range = re.findall(r"\d+", humidity)

        if len(humidity_range) == 2:
            humidity_min = humidity_range[0]
            humidity_max = humidity_range[1]

  plant_info["humidity_min_%"] = humidity_min
  plant_info["humidity_max_%"] = humidity_max

  plant_info["ph_min"] = ph_map[name][0]
  plant_info["ph_max"] = ph_map[name][0]

  print(plant_info)

    
if __name__ == "__main__":
  main()
