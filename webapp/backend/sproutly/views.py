'''
References:
https://docs.python.org/3/library/re.html
'''

import sys
import os

rpi_path = os.path.abspath(os.path.join(__file__, '../../../../rpi'))
sys.path.append(rpi_path)

# from plant_id_api import identify_plant
# TODO: rpi???

from django.shortcuts import render
import paho.mqtt.client as mqtt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sproutly.models import WebscrapedPlant, Plant, AutoSchedule
from soltech_scraping import webscrape_plant
import time
from sproutly.models import SensorData
import re

MQTT_SERVER = "broker.emqx.io"
MQTT_PORT = 1883
CONTROL_TOPIC = "django/sproutly/control"
MQTT_KEEPALIVE = 60


@csrf_exempt
def send_control_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        control_command = data.get("command")
        actuator = data.get("actuator")

        message = {
            "command": control_command,
            "actuator": actuator
        }

        print(f"publishing to {CONTROL_TOPIC}: {json.dumps(message)}")

        client = mqtt.Client()
        client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()
        client.publish(CONTROL_TOPIC, json.dumps(message))
        time.sleep(1)
        client.disconnect()

        return JsonResponse({"status": "Command Sent", "command": control_command, "actuator": actuator})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def get_user_plants(request):
    try:
        plants = Plant.objects.all().values("id", "name", "species", "image_url", "health_status")
        return JsonResponse(list(plants), safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "error": str(e)}, status=500)


# make species lowercase, remove special characters
def lowercase_species(species):
    return re.sub(r'[^\w\s]', '', species.lower())

@csrf_exempt
def add_user_plant(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            if data["species"] == "no-species":
                # plant species detection
                # TODO: change this to rpi code
                # best_match, common_names = identify_plant()
                best_match = "Dracaena masoniana (Chahin.) Byng & Christenh."
                common_names = ['Whale Fin Plant', 'Sansevieria Masoniana']
                lowercase_best_match = lowercase_species(best_match)
                lowercase_common_names = [lowercase_species(name) for name in common_names]

                # check if plant exists in webscraped database
                plants_in_db = WebscrapedPlant.objects.all()

                for plant_in_db in plants_in_db:
                    lowercase_plant_in_db = lowercase_species(plant_in_db.name)

                    if lowercase_best_match in lowercase_plant_in_db or lowercase_plant_in_db in lowercase_best_match:
                        # if exists, add to database
                        img_url = WebscrapedPlant.objects.get(name=plant_in_db.species).image_url

                        new_plant = Plant(
                            name = plant_in_db.name,
                            species = plant_in_db.species,
                            image_url = img_url,
                        )
                        new_plant.save()
                        
                        return JsonResponse({"status": "detected plant found", "species": plant_in_db.name}, status=200)
                    else:
                        for common_name in lowercase_common_names:
                            if common_name in lowercase_plant_in_db or lowercase_plant_in_db in common_name:
                                return JsonResponse({"status": "detected plant found", "species": plant_in_db.name}, status=200)
                    
                # if doesn't exist, allow manual auto scheduling
                new_plant = Plant(
                    name = data["name"],
                    species = best_match
                )
                new_plant.save()

                return JsonResponse({"status": "detected plant not found", "plantId": new_plant.id}, status=200)

            img_url = WebscrapedPlant.objects.get(name=data["species"]).image_url

            new_plant = Plant(
                name = data["name"],
                species = data["species"],
                image_url = img_url,
            )
            new_plant.save()

            # set up initial auto-schedule
            webscraped_plant = WebscrapedPlant.objects.get(name=data["species"])

            new_autoschedule = AutoSchedule(
                plant = new_plant,
                min_temp = webscraped_plant.temp_min,
                max_temp = webscraped_plant.temp_max,
                min_humidity = webscraped_plant.humidity_min,
                max_humidity = webscraped_plant.humidity_max,
                # light_frequency = 0,
                light_hours = webscraped_plant.light_duration,
                # water_frequency = 0,
                # water_amount = 0,
            )
            return JsonResponse({"status": "Success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
        
    return JsonResponse({"status": "Error", "error": "Invalid request"}, status=400)


@csrf_exempt
def update_manual_autoschedule(request):
    print("entered update_manual_autoschedule")
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            user_plant = Plant.objects.get(id=data["plantId"])

            if not AutoSchedule.objects.filter(plant=user_plant).exists():
                new_autoschedule = AutoSchedule(
                    plant = user_plant,
                    min_temp = data["schedule"]["minTemp"],
                    max_temp = data["schedule"]["maxTemp"],
                    min_humidity = data["schedule"]["minHumidity"],
                    max_humidity = data["schedule"]["maxHumidity"],
                    light_hours = data["schedule"]["lightHours"],
                    light_intensity = data["schedule"]["lightIntensity"],
                    water_frequency = data["schedule"]["waterFrequency"],
                    water_amount = data["schedule"]["waterAmount"],
                )
                new_autoschedule.save()
                return JsonResponse({"status": "Success"}, status=200)

            print("let's update schedule222")
            AutoSchedule.objects.filter(plant=user_plant).update(
                min_temp = data["schedule"]["minTemp"],
                max_temp = data["schedule"]["maxTemp"],
                min_humidity = data["schedule"]["minHumidity"],
                max_humidity = data["schedule"]["maxHumidity"],
                light_hours = data["schedule"]["lightHours"],
                light_intensity = data["schedule"]["lightIntensity"],
                water_frequency = data["schedule"]["waterFrequency"],
                water_amount = data["schedule"]["waterAmount"],
                # TODO: add other fields later
            )

            return JsonResponse({"status": "Success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    
    return JsonResponse({"status": "Error", "error": "Invalid request"}, status=400)

@csrf_exempt
def get_autoschedule(request, plant_id):
    try:
        autoschedule = AutoSchedule.objects.get(plant=Plant.objects.get(id=plant_id))
        autoschedule_json = {
            "min_temp": autoschedule.min_temp,
            "max_temp": autoschedule.max_temp,
            "min_humidity": autoschedule.min_humidity,
            "max_humidity": autoschedule.max_humidity,
            "light_intensity": autoschedule.light_intensity,
            "light_hours": autoschedule.light_hours,
            "water_frequency": autoschedule.water_frequency,
            "water_amount": autoschedule.water_amount
        }
        return JsonResponse(autoschedule_json, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    


@csrf_exempt
def get_plant_species(request):
    species = WebscrapedPlant.objects.all().values("index", "name")
    return JsonResponse(list(species), safe=False)

@csrf_exempt
def get_plant_info(request):
    if request.method != "POST":
        return JsonResponse({"status": "Error", "error": "Invalid request"}, status=400)
    try:
        data = json.loads(request.body)
        plant = WebscrapedPlant.objects.get(name=data["species"])

        plant_info = {
            "scientific_name": plant.scientific_name,
            "light_description": plant.light_description,
            "light_t0": plant.light_t0,
            "light_duration": plant.light_duration,
            "water_description": plant.water_description,
            "temp_min": plant.temp_min,
            "temp_max": plant.temp_max,
            "humidity_min": plant.humidity_min,
            "humidity_max": plant.humidity_max,
        }
        return JsonResponse(plant_info, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "error": str(e)}, status=500)
        

@csrf_exempt
# get detailed webscraped plant data and save to database
def get_webscraped_plant_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_plant_index = int(data["index"])

            plant = WebscrapedPlant.objects.get(index=selected_plant_index)
            plant_data = []
            plant_data.append(plant.name)
            plant_data.append(plant.image_url)
            plant_data.append(plant.info_url)

            if plant.temp_max: # meaning there's already webscraped data stored in db
                return JsonResponse({"status": "Success"}, status=200)

            scraped_data = webscrape_plant(plant_data, selected_plant_index)
            if not scraped_data:
                return JsonResponse({"error": "Failed to scrape data"}, status=500)
            
            plant.scientific_name = scraped_data["scientific_name"]
            plant.light_description = scraped_data["light_description"]
            plant.light_t0 = scraped_data["light_t0"]
            plant.light_duration = scraped_data["light_duration"]
            plant.water_description = scraped_data["water"]
            plant.temp_min = scraped_data["temp_min_F"]
            plant.temp_max = scraped_data["temp_max_F"]
            plant.humidity_min = scraped_data["humidity_min_%"]
            plant.humidity_max = scraped_data["humidity_max_%"]
            plant.save()

            return JsonResponse({"status": "Success"}, status=200)

        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)

    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)


@csrf_exempt
def get_sensor_data_history(request):
    data = list(SensorData.objects.all().values())
    
    for d in data:
        d["timestamp"] = d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return JsonResponse(data, safe=False)