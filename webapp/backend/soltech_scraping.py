''' 
This is a file to get the plant data by webscraping gardenia.net
Zara Mansoor (zmansoor)
Yuna Shin (yoonahs)

'''
import requests
from bs4 import BeautifulSoup
import re
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps.settings')
django.setup()

from sproutly.models import WebscrapedPlant

# function to web scrape detailed plant care info
def webscrape_plant(plant_data, plant_id):
  # name, img, url = plant_data[int(plant_id)]
  name, img, url = plant_data
  print(url)


  response = requests.get(url)
  
  if response.status_code != 200:
    print(response.status_code, " Failed to retrieve the page.")
    return dict()
  
  soup = BeautifulSoup(response.content, "html.parser")
  # scientific_name, light, watering ?, temp, humidity
  # still need pH and consistent watering system
  plant_info = dict()

  scientific_name = "n/a"
  scientific_name_tag = soup.find("strong", string=lambda text: text and "SCENTIFIC NAME" in text)
  if scientific_name_tag:
    # Get the parent <p> tag and then find the second <strong> inside it
    parent_span_sci = scientific_name_tag.find_parent("p")
    if parent_span_sci:
      scientific_name = parent_span_sci.get_text(strip=True).replace("SCENTIFIC NAME:", "").strip()

  plant_info["scientific_name"] = scientific_name

  # map of light_description: [light_t0, light_duration]
  light_map = {
    'Full Sun (Bright Direct Light) & High Light (Bright Indirect Light)': [6, 14],
    'High Light (Bright Indirect Light)': [7, 12], 
    'High Light (Bright Indirect Light); Low Light Tolerant': [8, 10],
    'Medium Light (Medium Indirect Light) to High Light (Bright Indirect Light)': [9, 8],
    'Medium Light (Medium Indirect Light) to High Light (Bright Indirect Light); Low Light Tolerant': [9, 6]
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
  plant_info["light_t0"] = light_map[light][0]
  plant_info["light_duration"] = light_map[light][1]

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


  print(plant_info)

  return plant_info


  # TODO: web scrape pH level data from other sources

  # # reference for plant pH level
  # url = f"https://soiltesting.cahnr.uconn.edu/plant-ph-preferences/"
  # print(url)

  # response = requests.get(url)
  
  # if response.status_code != 200:
  #   print(response.status_code, " Failed to retrieve the page.")
  #   return
  
  # soup = BeautifulSoup(response.content, "html.parser")
  # # print(soup.prettify())


# this has been run once to save all the plant names in db
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



  # save all the plant names
  for i in range(len(plant_data)):
    name, img, href = plant_data[i]
    WebscrapedPlant.objects.get_or_create(
      index = i,
      name = name,
      image_url = img,
      info_url = href
    )



    
if __name__ == "__main__":
  main()
