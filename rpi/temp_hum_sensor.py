import dht11
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

sensor = dht11.DHT11(pin=17)

while True:
    result = sensor.read()
    if result.is_valid():
        print(f"Temperature: {result.temperature} C")
        print(f"Humidity: {result.humidity} %")
    else:
        print("Failed to read from DHT11")
    time.sleep(2)