''' 
This is a file to get the input sensor data
Zara Mansoor (zmansoor)

Reference for dht11: https://pimylifeup.com/raspberry-pi-dht11-sensor/
Reference for MQTT: https://www.emqx.com/en/blog/how-to-use-mqtt-in-django
'''
import time
import adafruit_dht
import board
import paho.mqtt.client as mqtt
import json
import sys
import os
import logging
from datetime import datetime, timedelta
from plant_health.main import health_check
from gpiozero import OutputDevice
import serial

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
  sys.path.append(libdir)

from waveshare_TSL2591 import TSL2591

# MQTT configuration
MQTT_SERVER = "broker.emqx.io"  # use your broker address
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = "django/sproutly/mqtt"  # topic to send data to
HEALTH_TOPIC = "django/sproutly/health"
CONTROL_TOPIC = "django/sproutly/control" # topic to receive control commands from web app

# check sensor data once a minute
last_sensor_send_time = datetime.now() - timedelta(minutes=1)

# check plant health once a day
last_health_check_time = datetime.now() - timedelta(days=1)

# DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D17)

# soil moisture and light sensor data from arduino
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
soil_moisture = 0.0
lux = 0

# heater 
HEATER_RELAY_PIN = 23
heater_relay = OutputDevice(HEATER_RELAY_PIN)
heater_relay.on()

# water pump
WATER_PUMP_RELAY_PIN = 18
water_pump_relay = OutputDevice(WATER_PUMP_RELAY_PIN)
water_pump_relay.on()

# callback for when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected successfully to MQTT broker.")
    client.subscribe(CONTROL_TOPIC)
  else:
    print(f"Failed to connect to MQTT broker. Return code {rc}")

# callback for receiving control messages
def on_message(client, userdata, msg):
  print(f"msg.topics: {msg.topic}")
  try:
    raw_payload = msg.payload.decode()
    print(f"Received control message: {raw_payload}")
    control_command = json.loads(raw_payload)
    if control_command["command"] == "get_plant_health_check":
      send_plant_health(client)
    if control_command["command"] == "on":
      if control_command["actuator"] == "heater":
        print("heater on")
        heater_relay.off()
      if control_command["actuator"] == "water_pump":
        print("water pump on")
        water_pump_relay.off()
    if control_command["command"] == "off":
      if control_command["actuator"] == "heater":
        print("heater off")
        heater_relay.on()
      if control_command["actuator"] == "water_pump":
        print("water pump off")
        water_pump_relay.on()

  except json.JSONDecodeError as e:
    print("JSON Decode Error:", e)
    print("Invalid JSON received:", raw_payload)


def send_sensor_data(client, temperature_c, temperature_f, humidity, soil_moisture, lux):
  global last_sensor_send_time
  try:
    # create a JSON object with the temperature and humidity
    data = {
      "temperature_c": temperature_c,
      "temperature_f": temperature_f,
      "humidity": humidity,
      "soil_moisture": soil_moisture,
      "lux": lux
    }

    payload = json.dumps(data)

    # publish the data to the MQTT topic
    client.publish(MQTT_TOPIC, payload)
    print("Published sensor data:", payload)

    last_sensor_send_time = datetime.now()

  except Exception as e:
    print(f"Error in sending sensor data: {e}")


def send_plant_health(client):
  global last_health_check_time
  try:
    health_status = health_check()
    
    payload = json.dumps({
        "type": "plant_health",
        "status": health_status
    })
    
    client.publish(HEALTH_TOPIC, payload)
    print("Published plant health status:", payload)

    last_health_check_time = datetime.now()

  except Exception as e:
    print(f"Error in health check: {e}")

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
    if ser.in_waiting > 0:
      try:
        line = ser.readline().decode('utf-8').strip()
        values = line.split(',')
        if len(values) == 2:
          soil_moisture = float(values[0])
          lux = int(values[1])
      except ValueError: 
        print(f"Invalid data received")

    print("Temp:{:.1f} C / {:.1f} F Humidity: {}% Soil Moisture: {}% Light: {} lux".format(temperature_c, temperature_f, humidity, soil_moisture, lux))

    # check if 1 minute has passed since last sensor data was sent
    if datetime.now() - last_sensor_send_time >= timedelta(minutes=1):
      send_sensor_data(client, temperature_c, temperature_f, humidity, soil_moisture, lux)
    
    # check if 24 hours have passed since last health check
    if datetime.now() - last_health_check_time >= timedelta(days=1):
      send_plant_health(client)

  except RuntimeError as err:
    print(err.args[0])

  time.sleep(2.0)
