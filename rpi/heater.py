'''
This is file to control the heater from the RPi GPIO 23

Zara Mansoor (zmansoor)
'''
import time
import RPi.GPIO as GPIO

RELAY_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.HIGH)
print("Heater is ON")

time.sleep(2)

GPIO.output(RELAY_PIN, GPIO.LOW)
print("Heater is OFF")
GPIO.cleanup()