import paho.mqtt.client as mqtt
import json

MQTT_SERVER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "django/mqtt"
MQTT_KEEPALIVE = 60

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("Received Sensor Data:", data)

    # TODO: save data to database


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(
    host=MQTT_SERVER,
    port=MQTT_PORT,
    keepalive=MQTT_KEEPALIVE
)
