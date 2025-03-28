from django.shortcuts import render
import paho.mqtt.client as mqtt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sproutly.models import WebscrapedPlant
from soltech_scraping import webscrape_plant

MQTT_SERVER = "broker.emqx.io"
CONTROL_TOPIC = "django/sproutly/control"

@csrf_exempt
def send_control_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        control_command = data.get("command")
        actuator = data.get("actuator")

        client = mqtt.Client()
        client.connect(MQTT_SERVER, 1883)
        client.publish(CONTROL_TOPIC, json.dumps(control_command))
        client.disconnect()

        return JsonResponse({"status": "Command Sent", "command": control_command, "actuator": actuator})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def get_plant_species(request):
    species = WebscrapedPlant.objects.all().values("index", "name")
    return JsonResponse(list(species), safe=False)


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

    return JsonResponse({"error": "Invalid request"}, status=400)