import paho.mqtt.client as mqtt
import json
import os
import django

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
        print("Received Sensor Data:", data)

        # save sensor data to mysql db
        SensorData.objects.create(
            temperature_c = data["temperature_c"],
            temperature_f = data["temperature_f"],
            humidity = data["humidity"],
            # TODO: add more sensors later
        )

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

client.connect(
    host=MQTT_SERVER,
    port=MQTT_PORT,
    keepalive=MQTT_KEEPALIVE
)
