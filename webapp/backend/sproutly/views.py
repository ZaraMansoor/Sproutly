'''
References:
https://docs.python.org/3/library/re.html
'''


from django.shortcuts import render
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sproutly.models import WebscrapedPlant, Plant, AutoSchedule, PlantDetectionData
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



def set_up_autoschedule(number_of_plants, new_plant, webscraped_plant):

    new_autoschedule = AutoSchedule(
        number_of_plants = number_of_plants,
        plant = new_plant,
        min_temp = webscraped_plant.temp_min,
        max_temp = webscraped_plant.temp_max,
        min_humidity = webscraped_plant.humidity_min,
        max_humidity = webscraped_plant.humidity_max,
        # light_start_time: default (9am)
        light_intensity = webscraped_plant.light_intensity,
        # light_hours: default (9 hours)
        # water_frequency: default (once a week) -> has to be changed by a user
        # water_start_time: default (9am)
        # water_amount: default (100ml)
        # nutrients_start_time: default (9am)
        # nutrients_amount: default (2ml)
    )
    print("new autoschedule created!")
    new_autoschedule.save()
    print("new autoschedule saved!")
    

@csrf_exempt
def add_user_plant(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            user_plant_name = data["name"]
            species_selected = data["species"]
            number_of_plants = data["numberOfPlants"]

            if data["species"] == "no-species":
                # plant species detection

                # send a get_plant_id request to rpi (to get detected plant species data)
                publish.single(
                    topic="django/sproutly/mqtt",
                    payload=json.dumps({"command": "get_plant_id"}),
                    hostname="broker.emqx.io"
                )
                print("sent get_plant_id request to rpi")

                # wait? sleep?
                time.sleep(3) 

                print("let's check if we have received detection data from rpi")
                best_match = PlantDetectionData.objects.latest('timestamp').best_match
                common_names = PlantDetectionData.objects.latest('timestamp').common_names
                print("type(common_names): ", type(common_names))

                # TODO: comment out for TESTING
                # best_match = "Aloe Plant"
                # common_names = ['Whale Fin Plant', 'Sansevieria Masoniana']
                lowercase_best_match = lowercase_species(best_match)
                lowercase_common_names = [lowercase_species(name) for name in common_names]

                # check if plant exists in webscraped database
                plants_in_db = WebscrapedPlant.objects.all()

                for plant_in_db in plants_in_db:
                    lowercase_plant_in_db = lowercase_species(plant_in_db.name)

                    if lowercase_best_match in lowercase_plant_in_db or lowercase_plant_in_db in lowercase_best_match:
                        # (1) if exists, add to database
                        img_url = WebscrapedPlant.objects.get(name=plant_in_db.name).image_url

                        print("let's create a new plant (1)")
                        new_plant = Plant(
                            name = user_plant_name,
                            species = plant_in_db.name,
                            image_url = img_url,
                        )
                        print("new plant created11!")
                        new_plant.save()
                        print("new plant saved11!")

                        webscraped_plant = WebscrapedPlant.objects.get(name=plant_in_db.name)
                        print("got a webscraped plant")

                        # set up initial auto-schedule
                        set_up_autoschedule(number_of_plants, new_plant, webscraped_plant)

                        return JsonResponse({"status": "detected plant found", "species": plant_in_db.name}, status=200)
                    else:
                        for common_name in lowercase_common_names:
                            if common_name in lowercase_plant_in_db or lowercase_plant_in_db in common_name:
                                return JsonResponse({"status": "detected plant found", "species": plant_in_db.name, "number_of_plants": number_of_plants}, status=200)
                    
                # (2) if doesn't exist, allow manual auto scheduling
                print("let's create a new plant (2)")
                new_plant = Plant(
                    name = data["name"],
                    species = best_match
                )
                print("new plant created22!")
                new_plant.save()
                print("new plant saved22!")

                return JsonResponse({"status": "detected plant not found", "plantId": new_plant.id, "number_of_plants": number_of_plants}, status=200)

            img_url = WebscrapedPlant.objects.get(name=data["species"]).image_url

            print("let's create a new plant")
            new_plant = Plant(
                name = data["name"],
                species = data["species"],
                image_url = img_url,
            )
            new_plant.save()
            print("new plant created!")

            webscraped_plant = WebscrapedPlant.objects.get(name=species_selected)
            print("got a webscraped plant")

            # set up initial auto-schedule
            set_up_autoschedule(number_of_plants, new_plant, webscraped_plant)

            return JsonResponse({"status": "Success"}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
        
    return JsonResponse({"status": "Error", "error": "Invalid request"}, status=400)

    

@csrf_exempt
def update_manual_autoschedule(request):
    print("entered update_manual_autoschedule")
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            number_of_plants = data["numberOfPlants"]

            user_plant = Plant.objects.get(id=data["plantId"])

            if not AutoSchedule.objects.filter(plant=user_plant).exists():
                new_autoschedule = AutoSchedule(
                    plant = user_plant,
                    number_of_plants = number_of_plants,
                    min_temp = data["schedule"]["minTemp"],
                    max_temp = data["schedule"]["maxTemp"],
                    min_humidity = data["schedule"]["minHumidity"],
                    max_humidity = data["schedule"]["maxHumidity"],
                    light_start_time = data["schedule"]["lightStartTime"],
                    light_intensity = data["schedule"]["lightIntensity"],
                    light_hours = data["schedule"]["lightHours"],
                    water_frequency = data["schedule"]["waterFrequency"],
                    water_start_time = data["schedule"]["waterStartTime"],
                    water_amount = data["schedule"]["waterAmount"],
                    nutrients_start_time = data["schedule"]["nutrientsStartTime"],
                    nutrients_amount = data["schedule"]["nutrientsAmount"],
                )
                new_autoschedule.save()
                return JsonResponse({"status": "Success"}, status=200)

            print("let's update schedule222")
            AutoSchedule.objects.filter(plant=user_plant).update(
                min_temp = data["schedule"]["minTemp"],
                max_temp = data["schedule"]["maxTemp"],
                min_humidity = data["schedule"]["minHumidity"],
                max_humidity = data["schedule"]["maxHumidity"],
                light_start_time = data["schedule"]["lightStartTime"],
                light_intensity = data["schedule"]["lightIntensity"],
                light_hours = data["schedule"]["lightHours"],
                water_frequency = data["schedule"]["waterFrequency"],
                water_start_time = data["schedule"]["waterStartTime"],
                water_amount = data["schedule"]["waterAmount"],
                nutrients_start_time = data["schedule"]["nutrientsStartTime"],
                nutrients_amount = data["schedule"]["nutrientsAmount"],
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
            "number_of_plants": autoschedule.number_of_plants,
            "min_temp": autoschedule.min_temp,
            "max_temp": autoschedule.max_temp,
            "min_humidity": autoschedule.min_humidity,
            "max_humidity": autoschedule.max_humidity,
            "light_start_time": autoschedule.light_start_time,
            "light_intensity": autoschedule.light_intensity,
            "light_hours": autoschedule.light_hours,
            "water_frequency": autoschedule.water_frequency,
            "water_start_time": autoschedule.water_start_time,
            "water_amount": autoschedule.water_amount,
            "nutrients_start_time": autoschedule.nutrients_start_time,
            "nutrients_amount": autoschedule.nutrients_amount
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
            "light_intensity": plant.light_intensity,
            "water_description": plant.water_description,
            "temp_min": plant.temp_min,
            "temp_max": plant.temp_max,
            "humidity_min": plant.humidity_min,
            "humidity_max": plant.humidity_max,
            "ph_min": plant.ph_min,
            "ph_max": plant.ph_max,
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
            plant_name = data["plantName"]

            plant = WebscrapedPlant.objects.get(index=selected_plant_index)
            plant_data = []
            plant_data.append(plant.name)
            plant_data.append(plant.image_url)
            plant_data.append(plant.info_url)

            # TODO: Comment out for DEMOing purposes!!!
            # if plant.temp_max: # meaning there's already webscraped data stored in db
            #     return JsonResponse({"status": "Success"}, status=200)

            scraped_data = webscrape_plant(plant_data, selected_plant_index)
            if not scraped_data:
                return JsonResponse({"error": "Failed to scrape data"}, status=500)
            
            print("scraped_data", scraped_data)
            print("scraped_data['light_intensity']", scraped_data["light_intensity"])
            plant.scientific_name = scraped_data["scientific_name"]
            plant.light_description = scraped_data["light_description"]
            plant.light_intensity = scraped_data["light_intensity"]
            plant.water_description = scraped_data["water"]
            plant.temp_min = scraped_data["temp_min_F"]
            plant.temp_max = scraped_data["temp_max_F"]
            plant.humidity_min = scraped_data["humidity_min_%"]
            plant.humidity_max = scraped_data["humidity_max_%"]
            plant.ph_min = scraped_data["ph_min"]
            plant.ph_max = scraped_data["ph_max"]
            plant.save()

            print("plant!!: ", plant)
            # update the autoschedule to reflect the webscraped data
            user_plant = Plant.objects.get(name=plant_name)
            print("user_plant11: ", user_plant)
            plant_updated = AutoSchedule.objects.get(plant=user_plant)
            print("plant_updated22: ", plant_updated)

            plant_updated.min_temp = plant.temp_min
            plant_updated.max_temp = plant.temp_max
            plant_updated.min_humidity = plant.humidity_min
            plant_updated.max_humidity = plant.humidity_max
            plant_updated.light_intensity = plant.light_intensity
            plant_updated.save()

            return JsonResponse({"status": "Success"}, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)

    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)


@csrf_exempt
def get_sensor_data_history(request):
    print("")
    data = list(SensorData.objects.all().order_by("timestamp").values())
    data = data[:1440]

    print("data::::: ", data)
    
    for d in data:
        d["timestamp"] = d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return JsonResponse(data, safe=False)


@csrf_exempt
def change_automatic_or_manual(request):
    if request.method == "POST":
        try:
            print("entered")
            data = json.loads(request.body)

            curr_schedule = AutoSchedule.objects.get(id=data["plantId"])
            curr_schedule.automatic_mode = data["command"]
            curr_schedule.save()

            return JsonResponse({"status": "Success"}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)

@csrf_exempt
def get_automatic_or_manual(request):
    if request.method == "GET":
        try:
            curr_schedule = AutoSchedule.objects.get(id=1)
            return JsonResponse({"automatic_or_manual": curr_schedule.automatic_mode}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)



@csrf_exempt
def change_number_of_plants(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            fetched_plant = Plant.objects.get(id=data["plantId"])
            print("fetched_plant22: ", fetched_plant)
            curr_schedule = AutoSchedule.objects.get(plant=fetched_plant)
            print("curr_schedule22: ", curr_schedule)
            curr_schedule.number_of_plants = data["numberOfPlants"]
            curr_schedule.save()
            print("curr_schedule.number_of_plants: ", curr_schedule.number_of_plants)

            return JsonResponse({"status": "Success"}, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)


@csrf_exempt
def get_number_of_plants(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("data!! here: ", data)
            fetched_plant = Plant.objects.get(id=data["plantId"])
            print("fetched_plant: ", fetched_plant)
            curr_schedule = AutoSchedule.objects.get(plant=fetched_plant)
            print("curr_schedule: ", curr_schedule)
            return JsonResponse({"number_of_plants": curr_schedule.number_of_plants}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)


@csrf_exempt
def get_detection_result(request):
    if request.method == "GET":
        try:
            best_match = PlantDetectionData.objects.latest('timestamp').best_match
            common_names = PlantDetectionData.objects.latest('timestamp').common_names
            print("best_match22: ", best_match)
            print("common_names22: ", common_names)
            return JsonResponse({"best_match": best_match, "common_names": common_names}, status=200)
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)
    return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)


# @csrf_exempt
# def update_current_plant(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             fetched_plant = Plant.objects.get(id=data["plantId"])
#             if CurrPlant.objects.filter(user_id=1).exists():
#                 CurrPlant.objects.filter(user_id=1).delete()
#             new_current_plant = CurrPlant.objects.create(user_id=1, current_plant=fetched_plant)
#             new_current_plant.save()
#             return JsonResponse({"status": "Success"}, status=200)
#         except Exception as e:
#             return JsonResponse({"status": "Error", "error": str(e)}, status=500)
#     return JsonResponse({"status": "Error","error": "Invalid request"}, status=400)