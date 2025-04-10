''' 
This is a file to get the input sensor data
Zara Mansoor (zmansoor)

Reference for dht11: https://pimylifeup.com/raspberry-pi-dht11-sensor/
Reference for MQTT: https://www.emqx.com/en/blog/how-to-use-mqtt-in-django
'''
import os
import time
import paho.mqtt.client as mqtt
import json
import sys
import logging
from datetime import datetime, timedelta
from plant_health.main import health_check
from plant_id_api import identify_plant
from gpiozero import OutputDevice
import serial
import stream
from stream import picam2
from PIL import Image
import io
import RPi.GPIO as GPIO
import dht11

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
  sys.path.append(libdir)

from waveshare_TSL2591 import TSL2591

class Relay(OutputDevice):
  def __init__(self, pin, active_high=False):
    super().__init__(pin, active_high=active_high)

# MQTT configuration
MQTT_SERVER = "broker.emqx.io"  # use your broker address
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = "django/sproutly/mqtt"  # topic to send data to
CONTROL_TOPIC = "django/sproutly/control" # topic to receive control commands from web app
HEATER_RELAY_PIN = 23
WATER_PUMP_RELAY_PIN = 18
LED_1_RELAY_PIN = 26
LED_2_RELAY_PIN = 6
LED_3_RELAY_PIN = 5
LED_4_RELAY_PIN = 19
WHITE_LIGHT_RELAY_PIN = 16

# start the stream, keep track of if live streaming or not
stream.start_stream()
streaming = True

# check sensor data once a minute
last_sensor_send_time = datetime.now() - timedelta(minutes=1)

# check plant health once a day
last_health_check_time = datetime.now() - timedelta(days=1)

# reset serial buffer data every 2.3 seconds
last_reset_time = datetime.now() - timedelta(seconds=2.3)

# DHT11 sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
dht_instance = dht11.DHT11(pin=17)
temperature_c = 0
temperature_f = 0
humidity = 0

# soil moisture and light sensor data from arduino
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
soil_moisture = 0.0
lux = 0

# heater 
heater_relay = Relay(HEATER_RELAY_PIN, active_high=False)
heater_relay.off()

# water pump
water_pump_relay = Relay(WATER_PUMP_RELAY_PIN, active_high=False)
water_pump_relay.off()

# LED light
led_1_relay = Relay(LED_1_RELAY_PIN, active_high=False)
led_2_relay = Relay(LED_2_RELAY_PIN, active_high=False)
led_3_relay = Relay(LED_3_RELAY_PIN, active_high=False)
led_4_relay = Relay(LED_4_RELAY_PIN, active_high=False)
white_light_relay = Relay(WHITE_LIGHT_RELAY_PIN, active_high=False)
led_1_relay.off()
led_2_relay.off()
led_3_relay.off()
led_4_relay.off()
white_light_relay.off()

# keep track of LED light state
last_led_state = 0

# control how may leds currently on
def control_leds(num_leds):
  if num_leds > 0:
    led_1_relay.on()
  else:
    led_1_relay.off()

  if num_leds > 1:
    led_2_relay.on()
  else:
    led_2_relay.off()

  if num_leds > 2:
    led_3_relay.on()
  else:
    led_3_relay.off()

  if num_leds > 3:
    led_4_relay.on()
  else:
    led_4_relay.off()

# callback for when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected successfully to MQTT broker.")
    client.subscribe(CONTROL_TOPIC)
  else:
    print(f"Failed to connect to MQTT broker. Return code {rc}")

# callback for receiving control messages
def on_message(client, userdata, msg):
  global last_led_state
  print(f"msg.topics: {msg.topic}")
  try:
    raw_payload = msg.payload.decode()
    print(f"Received control message: {raw_payload}")
    control_command = json.loads(raw_payload)
    if control_command["command"] == "get_plant_health_check":
      send_plant_health(client)
    elif control_command["command"] == "get_plant_id":
      send_plant_id(client)
    elif "actuator" in control_command:
      if control_command["actuator"] == "heater":
        if control_command["command"] == "on":
          heater_relay.on()
        elif control_command["command"] == "off":
          heater_relay.off()
      elif control_command["actuator"] == "water_pump":
        if control_command["command"] == "on":
          water_pump_relay.on()
        elif control_command["command"] == "off":
          water_pump_relay.off()
      elif control_command["actuator"] == "white_light":
        if control_command["command"] == "on":
          white_light_relay.on()
          control_leds(0)
        elif control_command["command"] == "off":
          white_light_relay.off()
          # go back to prev led state 
          if last_led_state == 0:
            control_leds(0)
            last_led_state = 0
          elif last_led_state == 1:
            control_leds(1)
            white_light_relay.off()
            last_led_state = 1
          elif last_led_state == 2:
            control_leds(2)
            white_light_relay.off()
            last_led_state = 2
          elif last_led_state == 3:
            control_leds(3)
            white_light_relay.off()
            last_led_state = 3
          elif last_led_state == 4:
            control_leds(4)
            white_light_relay.off()
            last_led_state = 4
      elif control_command["actuator"] == "LED_light":
        if control_command["command"] == 0:
          control_leds(0)
          last_led_state = 0
        elif control_command["command"] == 1:
          control_leds(1)
          white_light_relay.off()
          last_led_state = 1
        elif control_command["command"] == 2:
          control_leds(2)
          white_light_relay.off()
          last_led_state = 2
        elif control_command["command"] == 3:
          control_leds(3)
          white_light_relay.off()
          last_led_state = 3
        elif control_command["command"] == 4:
          control_leds(4)
          white_light_relay.off()
          last_led_state = 4
      elif control_command["actuator"] == "live_stream":
        if control_command["command"] == "on":
          if not streaming:
            stream.start_stream()
          streaming = True
        elif control_command["command"] == "off":
          if streaming:
            stream.stop_stream()
          streaming = False

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
    # turn white light on and wait for 2 seconds for camera to adjust
    control_leds(0)
    white_light_relay.on()
    time.sleep(2)

    if streaming:
      # get frame from stream
      frame = stream.get_latest_frame()
      image = Image.open(io.BytesIO(frame))
    else:
      # capture image
      picam2.start()
      image = picam2.capture_array('main')
      image = Image.fromarray(image)
      image = image.convert('RGB')
      picam2.stop()

    health_status = health_check(image)

    # turn white light off
    white_light_relay.off()
    assert 0 <= last_led_state <= 4
    control_leds(last_led_state)
    
    payload = json.dumps({
        "type": "plant_health",
        "status": health_status
    })
    
    client.publish(MQTT_TOPIC, payload)
    print("Published plant health status:", payload)

    last_health_check_time = datetime.now()

  except Exception as e:
    print(f"Error in health check: {e}")


def send_plant_id(client):
  try:
    # turn white light on and wait for 2 seconds for camera to adjust
    control_leds(0)
    white_light_relay.on()
    time.sleep(2)
    
    if streaming:
      # get frame from stream
      frame = stream.get_latest_frame()
      image_stream = io.BytesIO(frame)
      picam2.capture_file(image_stream, format="jpeg")
      image_stream.seek(0)
    else:
      # capture image
      picam2.start()
      image_stream = io.BytesIO()
      picam2.capture_file(image_stream, format="jpeg")
      image_stream.seek(0)
      picam2.stop()
    
    files = [
        ('images', ('image.jpg', image_stream, 'image/jpeg'))
    ]
    
    # turn white light off
    white_light_relay.off()
    assert 0 <= last_led_state <= 4
    control_leds(last_led_state)
    
    best_match, common_names = identify_plant(files)
  
    payload = json.dumps({
        "type": "plant_id",
        "best_match": best_match,
        "common_names": common_names
    })
    
    client.publish(MQTT_TOPIC, payload)
    print("Published plant id:", payload)
  
  except Exception as e:
    print(f"Error in plant identification (api): {e}")


# initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

while True:
  try:
    try:
      dht_result = dht_instance.read()
      if dht_result.is_valid():
        temperature_c = dht_result.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dht_result.humidity
    except RuntimeError as err:
      print(err)

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
    
    # check if 2.3 seconds have passed since serial buffer reset
    if datetime.now() - last_reset_time >= timedelta(seconds=2.3):
      ser.reset_input_buffer()
      last_reset_time = datetime.now()

  except RuntimeError as err:
    print(err.args[0])

  time.sleep(2.0)

# TODO: remove once integrated with webapp
send_plant_id(client)