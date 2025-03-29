'''
This is file to control the heater from the RPi GPIO 23

Zara Mansoor (zmansoor)
'''
from gpiozero import OutputDevice
import time

RELAY_PIN = 23
relay = OutputDevice(RELAY_PIN)

while True:
  user_input = input("on or off? ").strip().lower()

  if user_input == 'on':
    relay.on()
    print("Heater is ON")
  elif user_input == 'off':
    relay.off()
    print("Heater is OFF")
  elif user_input == 'exit':
    print("Exiting program...")
    break
  else:
    print("Invalid input. Please type 'ON', 'OFF', or 'exit'.")
  
  time.sleep(1)
