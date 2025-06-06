'''
References: 
https://www.emqx.com/en/blog/how-to-use-mqtt-in-django
https://channels.readthedocs.io/en/stable/topics/channel_layers.html#
'''

import paho.mqtt.client as mqtt
import json
import os
import django
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()

from sproutly.models import SensorData, Plant, PlantDetectionData, CurrPlant


MQTT_SERVER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "django/sproutly/mqtt"
HEALTH_TOPIC = "django/sproutly/health"
MQTT_KEEPALIVE = 60

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)
    client.subscribe(HEALTH_TOPIC)

def on_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode()

        data = json.loads(raw_payload) 
        print("Received data!!!:", data)


        try: # sensor data received
            if "heater" in data:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "sproutly_actuator_status",
                    {
                        "type": "actuatorStatusUpdate",
                        "data": data,
                    }
                )
                print("received actuators status:", data)

            # check if sensor data > 1440, if so, delete old data
            # can be changed later? 1440 is based on 24 hours
            # if SensorData.objects.count() > 1440:
            #     num_to_delete = SensorData.objects.count() - 1440

                # SensorData.objects.order_by('timestamp')[:num_to_delete].delete()

            
            # save sensor data to curr plant db
            if CurrPlant.objects.filter(user_id=1).exists():
                curr_plant = CurrPlant.objects.get(user_id=1).current_plant
                curr_plant_id = curr_plant.id

                SensorData.objects.create(
                    temperature_c = data["temperature_c"],
                    temperature_f = data["temperature_f"],
                    humidity = data["humidity"],
                    soil_moisture = data["soil_moisture"],
                    lux = data["lux"],
                    ph = data["ph"],
                    soil_temp = data["soil_temp"],
                    conductivity = data["conductivity"],
                    nitrogen = data["nitrogen"],
                    phosphorus = data["phosphorus"],
                    potassium = data["potassium"],
                    plant = Plant.objects.get(id=curr_plant_id),
                )


                print("Saved Sensor Data. plant:", Plant.objects.get(id=curr_plant_id))

            # send sensor data to websocket
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                "sproutly_sensor_data",
                {
                    "type": "sensorDataUpdate",
                    "data": data,
                }
            )
            print("Received Sensor Data:", data)
        
        except KeyError as e: # health status received
            channel_layer = get_channel_layer()

            if 'best_match' in data:
                async_to_sync(channel_layer.group_send)(
                    "sproutly_plant_detection",
                    {
                        "type": "plantDetectionUpdate",
                        "data": data,
                    }
                )
                print("Received Plant Detection Data:", data)

                PlantDetectionData.objects.create(
                    best_match = data["best_match"],
                    common_names = data["common_names"],
                )
                print("Saved Plant Detection Data:", data)


            if 'status' in data:
                async_to_sync(channel_layer.group_send)(
                    "sproutly_health_status",
                    {
                        "type": "healthUpdate",
                        "data": data,
                    }
                )
                print("Received Health Data:", data)

                current_plant_id = CurrPlant.objects.get(user_id=1).current_plant_id

                Plant.objects.filter(id=current_plant_id).update( 
                    health_status=data["status"],
                    last_detected=str(data["time"])
                )
                print("Updated Plant Health Status:", data["status"])

            

        
        except Exception as e:
            print("Error saving sensor data!:", e)


    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Invalid JSON received:", raw_payload)
        
    # data = json.loads(msg.payload.decode())
    # print("Received Sensor Data:", data)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE)
# client.loop_forever()
client.loop_start()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()