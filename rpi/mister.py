import RPi.GPIO as GPIO
import time

MISTER_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(MISTER_PIN, GPIO.OUT)

def press_mister(press_count=1, delay_between=0.5):
    """Simulates pressing the mister button press_count times."""
    for _ in range(press_count):
        GPIO.output(MISTER_PIN, GPIO.HIGH)  # Close relay (press button)
        time.sleep(0.2)  # Duration of button press
        GPIO.output(MISTER_PIN, GPIO.LOW)   # Release relay
        if _ < press_count - 1:
            time.sleep(delay_between)  # Wait before next press

try:
    while True:
        user_input = input("Enter number of presses (1-3): ")
        if user_input in ["1", "2", "3"]:
            press_mister(int(user_input))
        else:
            print("Invalid input. Enter 1, 2, or 3.")

except KeyboardInterrupt:
    GPIO.cleanup()
