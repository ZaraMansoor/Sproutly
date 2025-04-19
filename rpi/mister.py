import RPi.GPIO as GPIO
import time

HUMIDIFIER_PIN_1 = 14
HUMIDIFIER_PIN_2 = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(HUMIDIFIER_PIN_1, GPIO.OUT)
GPIO.setup(HUMIDIFIER_PIN_2, GPIO.OUT)

def pulse_r():
    GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(HUMIDIFIER_PIN_1, GPIO.LOW)

def pulse_l():
    GPIO.output(HUMIDIFIER_PIN_2, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(HUMIDIFIER_PIN_2, GPIO.LOW)

def pulse():
    GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)
    GPIO.output(HUMIDIFIER_PIN_2, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(HUMIDIFIER_PIN_1, GPIO.LOW)
    GPIO.output(HUMIDIFIER_PIN_2, GPIO.LOW)

try:
    time.sleep(2)
    while True:
        print('turning on')
        pulse_l()
        time.sleep(5)
        print('turning off')
        pulse_l()
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
