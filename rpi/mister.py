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

# try:
#     time.sleep(2)
#     while True:
#         print('turning on')
#         pulse()
#         time.sleep(10)
#         print('turning off')
#         pulse()
#         time.sleep(10)
# except KeyboardInterrupt:
#     GPIO.cleanup()

prev_input = None
while True:
    user_input = input("0 for on, 1 for off").strip().lower()

    if user_input == '0':
        if prev_input == '1':
            pulse_r()
    
    elif user_input == '1':
        if prev_input is None or prev_input == '0':
            pulse_r()
    
    else:
        print('invalid input')

    time.sleep(1)