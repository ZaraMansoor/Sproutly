'''
This is file to control the heater from the RPi GPIO 23

Zara Mansoor (zmansoor)
'''
import time
from gpiozero import OutputDevice

relay = OutputDevice(23)  # GPIO pin 23

relay.on()
print("Heater is ON")

time.sleep(2)

relay.off()
print("Heater is OFF")