import pigpio
import time
import dht11

pi = pigpio.pi()
sensor = dht11.DHT11(pin=17)  # GPIO17

while True:
  result = sensor.read()
  if result[0] == dht11.DHT11.OK:
    print(f"Temp: {result[1]} C  Humidity: {result[2]}%")
  else:
    print("Failed to read.")
  time.sleep(2)