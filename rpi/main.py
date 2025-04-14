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
from pymodbus.client import ModbusSerialClient
import requests

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

# soil moisture and light sensor data from arduino
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()

# 7-in-1 soil sensor 
soil_client = ModbusSerialClient(
  port="/dev/ttyUSB0",                   # Serial port for rpi
  baudrate=9600,                         # Baudrate for communication
  bytesize=8,                            # Number of bits per byte
  parity="N",                            # No parity
  stopbits=1,                            # One stop bit
)

soil_connected = soil_client.connect()
if soil_connected:
  print("Connected to soil sensor.")
else:
  print("Failed to connect to soil sensor.")

# actuators
actuators_status = {
  "heater": "off",
  "water_pump": "off",
  "nutrients_pump": "off",
  "mister": "off",
  "white_light": "off",
  "LED_light": 0,
  "live_stream": "on",
}

# heater 
heater_relay = Relay(HEATER_RELAY_PIN, active_high=False)
heater_relay.off()

# water pump
water_pump_relay = Relay(WATER_PUMP_RELAY_PIN, active_high=False)
water_pump_relay.off()

# nutrients pump 
NUTRIENTS_PUMP_RELAY_PIN = 24
nutrients_pump_relay = Relay(NUTRIENTS_PUMP_RELAY_PIN, active_high=False)
nutrients_pump_relay.off()

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
  global streaming
  print(f"msg.topics: {msg.topic}")
  try:
    raw_payload = msg.payload.decode()
    print(f"Received control message: {raw_payload}")
    control_command = json.loads(raw_payload)
    if control_command["command"] == "get_plant_health_check":
      send_plant_health(client)
    elif control_command["command"] == "get_plant_id":
      send_plant_id(client)
    elif control_command["command"] == "get_actuators_status":
      send_actuators_status(client)
    elif "actuator" in control_command:
      if control_command["actuator"] == "heater":
        if control_command["command"] == "on":
          heater_relay.on()
          actuators_status["heater"] = "on"
        elif control_command["command"] == "off":
          heater_relay.off()
          actuators_status["heater"] = "off"
      elif control_command["actuator"] == "water_pump":
        if control_command["command"] == "on":
          water_pump_relay.on()
          actuators_status["water_pump"] = "on"
        elif control_command["command"] == "off":
          water_pump_relay.off()
          actuators_status["water_pump"] = "off"
      elif control_command["actuator"] == "nutrients_pump":
        if control_command["command"] == "on":
          nutrients_pump_relay.on()
          actuators_status["nutrients_pump"] = "on"
        elif control_command["command"] == "off":
          nutrients_pump_relay.off()
          actuators_status["nutrients_pump"] = "off"
      elif control_command["actuator"] == "white_light":
        if control_command["command"] == "on":
          white_light_relay.on()
          control_leds(0)
          actuators_status["white_light"] = "on"
          actuators_status["LED_light"] = 0
        elif control_command["command"] == "off":
          white_light_relay.off()
          # go back to prev led state 
          control_leds(last_led_state)
          actuators_status["white_light"] = "off"
          actuators_status["LED_light"] = last_led_state
      elif control_command["actuator"] == "LED_light":
        control_leds(control_command["command"])
        last_led_state = control_command["command"]
        actuators_status["LED_light"] = control_command["command"]
        if control_command["command"] > 0:
          white_light_relay.off()
          actuators_status["white_light"] = "off"
      elif control_command["actuator"] == "live_stream":
        if control_command["command"] == "on":
          if not streaming:
            stream.start_stream()
          streaming = True
          actuators_status["live_stream"] = "on"
        elif control_command["command"] == "off":
          if streaming:
            stream.stop_stream()
          streaming = False
          actuators_status["live_stream"] = "off"

  except json.JSONDecodeError as e:
    print("JSON Decode Error:", e)
    print("Invalid JSON received:", raw_payload)


def send_sensor_data(client, sensor_data):
  global last_sensor_send_time
  try:
    # create a JSON object with the sensor data
    payload = json.dumps(sensor_data)

    # publish the data to the MQTT topic
    client.publish(MQTT_TOPIC, payload)
    print("Published sensor data:", payload)

    last_sensor_send_time = datetime.now()

  except Exception as e:
    print(f"Error in sending sensor data: {e}")


def send_plant_health(client):
  global last_health_check_time
  global streaming
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
  global streaming
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


def send_actuators_status(client):
  global actuators_status
  try:
    # create a JSON object with the actuator data
    payload = json.dumps(actuators_status)

    # publish the data to the MQTT topic
    client.publish(MQTT_TOPIC, payload)
    print("Published actuator data:", payload)

  except Exception as e:
    print(f"Error in sending actuator data: {e}")


def get_soil_sensor_data(sensor_data):
  ph_response = soil_client.read_holding_registers(address=0x06, count=1, slave=1)
  if not ph_response.isError():
    sensor_data["ph"] = ph_response.registers[0] / 100.0

  temp_moist_response = soil_client.read_holding_registers(address=0x12, count=2, slave=1)
  if not temp_moist_response.isError():
    sensor_data["soil_moisture_1"] = temp_moist_response.registers[0] / 10.0
    sensor_data["soil_temp"] = temp_moist_response.registers[1] / 10.0

  conductivity_response = soil_client.read_holding_registers(address=0x15, count=1, slave=1)
  if not conductivity_response.isError():
    sensor_data["conductivity"] = conductivity_response.registers[0]

  npk_response = soil_client.read_holding_registers(address=0x1e, count=3, slave=1)
  if not npk_response.isError():
    sensor_data["nitrogen"] = npk_response.registers[0]
    sensor_data["phosphorus"] = npk_response.registers[1]
    sensor_data["potassium"] = npk_response.registers[2]
  
  return (sensor_data)

# initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

sensor_data = {
  "temperature_c": 0,
  "temperature_f": 0,
  "humidity": 0,
  "soil_moisture": 0,
  "lux": 0,
  "ph": 0,
  "soil_moisture_1": 0,
  "soil_temp": 0,
  "conductivity": 0,
  "nitrogen": 0,
  "phosphorus": 0,
  "potassium": 0,
}

try:
  while True:
    try:
      # get dht11 sensor data
      try:
        dht_result = dht_instance.read()
        if dht_result.is_valid():
          sensor_data['temperature_c'] = dht_result.temperature
          sensor_data['temperature_f'] = sensor_data['temperature_c'] * (9 / 5) + 32
          sensor_data['humidity'] = dht_result.humidity
      except RuntimeError as err:
        print(err)

      # get arduino sensor data
      if ser.in_waiting > 0:
        try:
          line = ser.readline().decode('utf-8').strip()
          values = line.split(',')
          if len(values) == 2:
            sensor_data['soil_moisture'] = float(values[0])
            sensor_data['lux'] = int(values[1])
        except ValueError: 
          print(f"Invalid data received")

      # get 7-in-1 soil sensor data
      sensor_data = get_soil_sensor_data(sensor_data)

      print(
      f"Temp: {sensor_data['temperature_c']:.1f}°C / {sensor_data['temperature_f']:.1f}°F | "
      f"Humidity: {sensor_data['humidity']}% | "
      f"Soil Moisture: {sensor_data['soil_moisture']}% | "
      f"Light: {sensor_data['lux']} lux | "
      f"Soil pH: {sensor_data['ph']} pH | "
      f"Soil Temp: {sensor_data['soil_temp']}°C | "
      f"Soil Moisture 7-in-1: {sensor_data['soil_moisture_1']} RH% | "
      f"Conductivity: {sensor_data['conductivity']} µS/cm | "
      f"N: {sensor_data['nitrogen']} mg/kg | "
      f"P: {sensor_data['phosphorus']} mg/kg | "
      f"K: {sensor_data['potassium']} mg/kg"
      )

      # check if 1 minute has passed since last sensor data was sent
      if datetime.now() - last_sensor_send_time >= timedelta(minutes=1):
        send_sensor_data(client, sensor_data)
      
      # check if 24 hours have passed since last health check
      if datetime.now() - last_health_check_time >= timedelta(days=1):
        send_plant_health(client)
        
        # TODO: remove once integrated with webapp
        time.sleep(2)
        send_plant_id(client)
      
      # check if 2.3 seconds have passed since serial buffer reset
      if datetime.now() - last_reset_time >= timedelta(seconds=2.3):
        ser.reset_input_buffer()
        last_reset_time = datetime.now()

      
      # TODO: test later!!!!!

      # auto control running
      plant_id = 1 # hardcoded
      print("hereeee")
      schedule = requests.get(f"https://172.26.192.48:8443/get-autoschedule/{plant_id}/", verify=False).json()
      print("here22")
      # TODO: send auto control command
      # lights, water are turned on every noon
      curr_time = datetime.now().time()
      print("curr_time: ", curr_time)

      # if sensor_data['temperature_f'] < schedule["min_temp"]:
      #   heater_relay.on()
      #   actuators_status["heater"] = "on"
      # elif sensor_data['temperature_f'] > schedule["max_temp"]:
      #   heater_relay.off()
      #   actuators_status["heater"] = "off"

      if curr_time == datetime.strptime("11:33:00", "%H:%M:%S").time():
        water_pump_relay.on()
        actuators_status["water_pump"] = "on"
        if schedule["light_intensity"] == 1:
          led_1_relay.on()
          actuators_status["LED_light"] = 1
        elif schedule["light_intensity"] == 2:
          led_1_relay.on()
          led_2_relay.on()
          actuators_status["LED_light"] = 2
        elif schedule["light_intensity"] == 3:
          led_1_relay.on()
          led_2_relay.on()
          led_3_relay.on()
          actuators_status["LED_light"] = 3
        elif schedule["light_intensity"] == 4:
          led_1_relay.on()
          led_2_relay.on()
          led_3_relay.on()
          led_4_relay.on()
          actuators_status["LED_light"] = 4
        # TODO: add more actuators later

      
      # water_off_time = datetime.strptime("11:33:00", "%H:%M:%S").time() + timedelta(hours=schedule["water_frequency"]) # FIX!!! bug
      # if curr_time == water_off_time:
      #   water_pump_relay.off()
      #   actuators_status["water_pump"] = "off" # TODO: water pump how many ml??
      
      light_start_datetime = datetime.combine(datetime.now().date(), datetime.strptime("11:33:00", "%H:%M:%S").time())
      print("light_start_datetime: ", light_start_datetime)
      light_off_time = (light_start_datetime + timedelta(hours=schedule["light_hours"]/100)).time() # for testing
      print("light_off_time: ", light_off_time)
      print("vs curr_time: ", curr_time)
      if curr_time == light_off_time:
        if actuators_status["LED_light"] == 1:
          led_1_relay.off()
          actuators_status["LED_light"] = 0
        elif actuators_status["LED_light"] == 2:
          led_1_relay.off()
          led_2_relay.off()
          actuators_status["LED_light"] = 0
        elif actuators_status["LED_light"] == 3:
          led_1_relay.off()
          led_2_relay.off()
          led_3_relay.off()
          actuators_status["LED_light"] = 0
        elif actuators_status["LED_light"] == 4:
          led_1_relay.off()
          led_2_relay.off()
          led_3_relay.off()
          led_4_relay.off()
          actuators_status["LED_light"] = 0

  


    except RuntimeError as err:
      print(err.args[0])

    time.sleep(2.0)

except KeyboardInterrupt:
  if soil_connected:
    soil_client.close()
  GPIO.cleanup()