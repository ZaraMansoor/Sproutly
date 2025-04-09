import os
os.environ["BLINKA_FORCE_SW_PIN"] = "1"

import board
import adafruit_dht
import time

dht = adafruit_dht.DHT11(board.D17)

while True:
    try:
        temp = dht.temperature
        humidity = dht.humidity
        print(f"Temp: {temp}C  Humidity: {humidity}%")
    except RuntimeError as e:
        print(f"Runtime error: {e}")
    time.sleep(2)
