import RPi.GPIO as GPIO
import time

HUMIDIFIER_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(HUMIDIFIER_PIN, GPIO.OUT)

def pulse():
    GPIO.output(HUMIDIFIER_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(HUMIDIFIER_PIN, GPIO.LOW)

try:
    time.sleep(2)
    while True:
        print('turning on')
        pulse()
        time.sleep(3600)
        print('turning off')
        pulse()
        time.sleep(3600)
except KeyboardInterrupt:
    GPIO.cleanup()
