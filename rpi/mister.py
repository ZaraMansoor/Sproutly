# from gpiozero import OutputDevice
# import time

# class Relay(OutputDevice):
#     def __init__(self, pin, active_high=False):
#         super().__init__(pin, active_high=active_high)

# # using GPIO pin 14
# mister = Relay(14, active_high=True)


# def press_mister(press_count=1, delay_between=1.0):
#     """Simulates pressing the mister button press_count times."""
#     for _ in range(press_count):
#         mister.on()
#         time.sleep(1.0)
#         mister.off()
#         if _ < press_count - 1:
#             time.sleep(delay_between)

# while True:
#     user_input = input("Enter number of presses (1-3): ")
#     if user_input in ["1", "2", "3"]:
#         press_mister(int(user_input))
#     else:
#         print("Invalid input. Enter 1, 2, or 3.")


# while True:
#     user_input = input("Mister on or off: ")
#     if user_input in ["on"]:
#         mister.on()
#     elif user_input in ["off"]:
#         mister.off()
#     else:
#         print("Invalid input. Enter on or off")


import RPi.GPIO as GPIO
import time

HUMIDIFIER_PIN = 14  

GPIO.setmode(GPIO.BCM)
GPIO.setup(HUMIDIFIER_PIN, GPIO.OUT)

def pulse():
    GPIO.output(HUMIDIFIER_PIN, GPIO.HIGH)
    time.sleep(0.1)  # 100ms pulse
    GPIO.output(HUMIDIFIER_PIN, GPIO.LOW)

try:
    time.sleep(2)
    while True:
        print('turning on')
        pulse()
        time.sleep(5)
        print('turning off')
        pulse()
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
