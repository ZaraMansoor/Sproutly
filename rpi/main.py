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
# from plant_health.main import health_check
from plant_health.main_fusion import health_check
from plant_id_api import identify_plant
from gpiozero import OutputDevice
import serial
# import stream_latency as stream
# from stream_latency import picam2
import stream
from stream import picam2
from PIL import Image
import io
import RPi.GPIO as GPIO
import dht11
from pymodbus.client import ModbusSerialClient
import requests
import threading
import csv

# ---- Relay Class ----
# turns on and off relays through rpi gpio
class Relay(OutputDevice):
  def __init__(self, pin, active_high=False):
    super().__init__(pin, active_high=active_high)

# ---- Globals ----
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
MISTER_RELAY_PIN = 21
NUTRIENTS_PUMP_RELAY_PIN = 24
log_file_path = "sensor_actuator_log.csv"

# start the stream, keep track of if live streaming or not
stream.start_stream()
streaming = True

# check sensor data once a minute
last_sensor_send_time = datetime.now() - timedelta(minutes=1)

# check plant health once a day
last_health_check_time = datetime.now() - timedelta(days=1) + timedelta(seconds=3)

# reset serial buffer data every 2.3 seconds
last_reset_time = datetime.now() - timedelta(seconds=2.3)

# DHT11 sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
dht_instance = dht11.DHT11(pin=17)

# soil moisture and light sensor data from arduino
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
ser.reset_input_buffer()

# sent actuator status to arduino 2
ser2 = serial.Serial('/dev/ttyACM0', 19200, timeout=1)
ser2.reset_input_buffer()

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

# automatic control
automatic = True
running = True

# Actuators
actuators_status = {
  "heater": "off",
  "water_pump": "off",
  "nutrients_pump": "off",
  "mister": "off",
  "white_light": "off",
  "LED_light": 0,
  "live_stream": "on",
}

# mister
mister_relay = Relay(MISTER_RELAY_PIN, active_high=False)
mister_relay.off()

# heater 
heater_relay = Relay(HEATER_RELAY_PIN, active_high=False)
heater_relay.off()

# water pump
water_pump_relay = Relay(WATER_PUMP_RELAY_PIN, active_high=False)
water_pump_relay.off()

# nutrients pump 
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

# ---- Control and MQTT Functions ----

def initialize_csv():
  if not os.path.exists(log_file_path):
    with open(log_file_path, mode='w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow([
        "timestamp",
        *sensor_data.keys(),
        *actuators_status.keys()
      ])

def log_data():
  with open(log_file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    row = [
      datetime.now().isoformat(),
      *[sensor_data[key] for key in sensor_data],
      *[actuators_status[key] for key in actuators_status]
    ]
    writer.writerow(row)

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
  global automatic
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
    elif control_command["command"] == "automatic":
      automatic = True
    elif control_command["command"] == "manual":
      automatic = False
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
      elif control_command["actuator"] == "mister":
        if control_command["command"] == "on":
          mister_relay.on()
          actuators_status["mister"] = "on"
        elif control_command["command"] == "off":
          mister_relay.off()
          actuators_status["mister"] = "off"

    send_LED_actuator_status(actuators_status, health_status)

  except json.JSONDecodeError as e:
    print("JSON Decode Error:", e)
    print("Invalid JSON received:", raw_payload)

# initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

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


health_status = None
def send_plant_health(client):
  global last_health_check_time
  global streaming
  global health_status
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

    ordered_data = [
      sensor_data["soil_moisture"],
      sensor_data["temperature_c"],
      sensor_data["humidity"],
      sensor_data["lux"],
      sensor_data["ph"],
      sensor_data["nitrogen"],
      sensor_data["phosphorus"],
      sensor_data["potassium"],
    ]
    health_status = health_check(image, ordered_data)

    # turn white light off
    white_light_relay.off()
    assert 0 <= last_led_state <= 4
    control_leds(last_led_state)
    
    payload = json.dumps({
      "type": "plant_health",
      "status": health_status,
      "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    client.publish(MQTT_TOPIC, payload)
    print("Published plant health status:", payload)

    last_health_check_time = datetime.now()
    send_LED_actuator_status(actuators_status, health_status)

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

def send_LED_actuator_status(actuators_status, health_status):
  status_map = {
    "light": "lightOn" if actuators_status["LED_light"] > 0 or actuators_status["white_light"] == "on" else "lightOff",
    "water": "waterOn" if actuators_status["water_pump"] == "on" else "waterOff",
    "heater": "heaterOn" if actuators_status["heater"] == "on" else "heaterOff",
    "health": "healthy" if health_status == "Healthy" else "unhealthy"
  }

  for cmd in status_map.values():
    ser2.write(f"{cmd}\n".encode('utf-8'))

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

def control_loop():
  global running, soil_client, stream, sensor_data, last_reset_time
  water_pump_started = False
  water_pump_start_time = None

  nutrients_pump_started = False
  nutrients_pump_start_time = None
  while running:
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
        print("Sending sensor data")
        send_sensor_data(client, sensor_data)
        print("Sent sensor data")
      
      # check if 24 hours have passed since last health check
      if datetime.now() - last_health_check_time >= timedelta(days=1):
        print("Sending health data")
        send_plant_health(client)
        print("Sent health data")
      
      # check if 2.3 seconds have passed since serial buffer reset
      if datetime.now() - last_reset_time >= timedelta(seconds=2.3):
        print("reseting ip buffer")
        ser.reset_input_buffer()
        print("reset ip buffer")
        last_reset_time = datetime.now()

      # Automatic or manual control
      if automatic:
        print("Auto mode - processing sensors and relays...")
        # auto control running
        plant_id = 1 # hardcoded
        print("getting schedule")
        schedule = requests.get(f"https://172.26.192.48:8443/get-autoschedule/{plant_id}/", verify=False).json()
        print("got schedule")
        # schedule = {
        #   "number_of_plants": 3,
        #   "min_temp": 60,
        #   "max_temp": 75,
        #   "min_humidity": 60,
        #   "max_humidity": 80,
        #   "light_start_time": "09:00:00",
        #   "light_hours": 8,
        #   "light_intensity": 4,
        #   "water_amount": 250, 
        #   "water_start_time": "09:00:00",
        #   "nutrients_amount": 2, 
        #   "nutrients_start_time": "09:00:00",

        # }
        curr_time = datetime.now().time()
        print("got curr time")
        # Heater
        if sensor_data['temperature_f'] < schedule["min_temp"]:
          heater_relay.on()
          actuators_status["heater"] = "on"
        elif sensor_data['temperature_f'] > schedule["max_temp"]:
          heater_relay.off()
          actuators_status["heater"] = "off"
        print("heater done")
        # Mister
        if sensor_data['humidity'] < schedule["min_humidity"]:
          if actuators_status["mister"] == "off":
            mister_relay.on()
          actuators_status["mister"] = "on"
        elif sensor_data['humidity'] > schedule["max_humidity"]:
          if actuators_status["mister"] == "on":
            mister_relay.off()
          actuators_status["mister"] = "off"
        print("mister done")
        # Lights
        light_start_time = datetime.strptime(schedule["light_start_time"], "%H:%M:%S").time()
        light_end_time = (datetime.combine(datetime.today(), light_start_time) + timedelta(hours=schedule["light_hours"])).time()

        if light_start_time <= curr_time <= light_end_time:
          control_leds(schedule["light_intensity"])
          actuators_status["LED_light"] = schedule["light_intensity"]
        else:
          control_leds(0)
          actuators_status["LED_light"] = 0
        print("lights done")
        # Water and Nutrients
        water_duration = (100 / 250) * schedule["water_amount"] * schedule["number_of_plants"]
        nutrients_duration = (100 / 250) * schedule["nutrients_amount"] * (schedule["water_amount"] / 100) * schedule["number_of_plants"]

        if curr_time.strftime("%H:%M:%S") == schedule["water_start_time"]:
          water_pump_relay.on()
          actuators_status["water_pump"] = "on"
          water_pump_start_time = datetime.now()
          water_pump_started = True

        if curr_time.strftime("%H:%M:%S") == schedule["nutrients_start_time"]:
          nutrients_pump_relay.on()
          actuators_status["nutrients_pump"] = "on"
          nutrients_pump_start_time = datetime.now()
          nutrients_pump_started = True
          
        if water_pump_started and (datetime.now() - water_pump_start_time).total_seconds() >= water_duration:
          water_pump_relay.off()
          actuators_status["water_pump"] = "off"
          water_pump_started = False

        if nutrients_pump_started and (datetime.now() - nutrients_pump_start_time).total_seconds() >= nutrients_duration:
          nutrients_pump_relay.off()
          actuators_status["nutrients_pump"] = "off"
          nutrients_pump_started = False
        print("water and nutrients done")
        send_LED_actuator_status(actuators_status, health_status)
        print("sent status")
      else:
        print("Manual mode - waiting for controls")

    except RuntimeError as err:
      print(err.args[0])

    log_data()
    time.sleep(1)
  print("[THREAD] Control loop exited.")

def main():
  global running, soil_client, stream
  initialize_csv()
  # start control loop in a background thread
  control_thread = threading.Thread(target=control_loop)
  control_thread.daemon = True
  control_thread.start()

  try:
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    client.loop_start()
    while running:
      time.sleep(1)

  except KeyboardInterrupt:
    print("Exiting...")
    running = False
    client.loop_stop()
    client.disconnect() 
    control_thread.join()
    if soil_connected:
      soil_client.close()
    if (streaming):
      stream.stop_stream()
    time.sleep(1)
    GPIO.cleanup()

if __name__ == "__main__":
  main()