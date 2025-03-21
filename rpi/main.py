''' 
This is a file to get the input sensor data
Zara Mansoor (zmansoor)

Reference for dht11: https://pimylifeup.com/raspberry-pi-dht11-sensor/
'''
import time
import adafruit_dht
import board
import paho.mqtt.client as mqtt
import json

# MQTT configuration
MQTT_SERVER = "broker.emqx.io"  # use your broker address
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = "django/sproutly/mqtt"  # topic to send data to
CONTROL_TOPIC = "django/control" # topic to receive control commands from web app

#DHT11 sensor

dht_device = adafruit_dht.DHT11(board.D4)

# callback for when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected successfully to MQTT broker.")
    client.subscribe(CONTROL_TOPIC)
  else:
    print(f"Failed to connect to MQTT broker. Return code {rc}")

# callback for receiving control messages
def on_message(client, userdata, msg):
  print(f"Received control message: {msg.payload.decode()}")
  control_command = json.loads(msg.payload.decode())

 # if control_command["command"] == "water": # TODO: implement


# initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

while True:
  try:
    temperature_c = dht_device.temperature
    temperature_f = temperature_c * (9 / 5) + 32
    humidity = dht_device.humidity

    print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))

    # create a JSON object with the temperature and humidity
    data = {
      "temperature_c": temperature_c,
      "temperature_f": temperature_f,
      "humidity": humidity
    }

    payload = json.dumps(data)

    # publish the data to the MQTT topic
    client.publish(MQTT_TOPIC, payload)
    
  except RuntimeError as err:
    print(err.args[0])

  time.sleep(2.0)
