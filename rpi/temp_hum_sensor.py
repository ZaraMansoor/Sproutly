import RPi.GPIO as GPIO
import dht11
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

instance = dht11.DHT11(pin=17)

try:
  while True:
    result = instance.read()
    if result.is_valid():
      print(f"Temp: {result.temperature}C  Humidity: {result.humidity}%")
    else:
      print(":(")
    time.sleep(2)
except KeyboardInterrupt:
  print("Cleanup")
  GPIO.cleanup()
