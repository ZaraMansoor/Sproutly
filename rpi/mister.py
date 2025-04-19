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

while True:
    try:
        user_input = input("0 = all off; 1 = mister 1 on; 2 = mister 2 on; 3 = both misters on").strip().lower()

        if user_input == '0':
            print("all OFF")
        elif user_input == '1':
            pulse_l()
            print("water pump is ON")
        elif user_input == '2':
            pulse_r()
            print("nutrients pump is ON")
        elif user_input == '3':
            pulse_l()
            pulse_r()
            print("all ON")
        elif user_input == 'exit':
            print("Exiting program...")
            break
        else:
            print("Invalid input. Please type 'ON', 'OFF', or 'exit'.")
    
        time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()

    # time.sleep(2)
    # while True:
    #     print('turning on')
    #     pulse_l()
    #     time.sleep(5)
    #     print('turning off')
    #     pulse_l()
    #     time.sleep(5)

