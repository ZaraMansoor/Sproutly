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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
django.setup()

from sproutly.models import SensorData


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
        print("Raw MQTT Payload:", raw_payload)

        data = json.loads(raw_payload) 
        print("Received Sensor/Health Data:", data)


        try: # sensor data received

            # check if sensor data > 1440, if so, delete old data
            # TODO: can be changed later? 1440 is based on 24 hours
            if SensorData.objects.count() > 1440:
                num_to_delete = SensorData.objects.count() - 1440
                SensorData.objects.order_by('timestamp')[:num_to_delete].delete()

            # save sensor data to mysql db
            SensorData.objects.create(
                temperature_c = data["temperature_c"],
                temperature_f = data["temperature_f"],
                humidity = data["humidity"],
                # TODO: add more sensors later
            )

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

            async_to_sync(channel_layer.group_send)(
                "sproutly_health_status",
                {
                    "type": "healthUpdate",
                    "data": data,
                }
            )
            print("Received Health Data:", data)
        
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
client.loop_forever()
