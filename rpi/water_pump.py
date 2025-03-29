'''
This is file to control the water pump from the RPi GPIO 18

Zara Mansoor (zmansoor)
'''
from gpiozero import OutputDevice
import time

RELAY_PIN = 18
relay = OutputDevice(RELAY_PIN)
relay.off()

while True:
  user_input = input("on or off? ").strip().lower()

  if user_input == 'on':
    relay.on()
    print("water pump is ON")
  elif user_input == 'off':
    relay.off()
    print("water pump is OFF")
  elif user_input == 'exit':
    print("Exiting program...")
    break
  else:
    print("Invalid input. Please type 'ON', 'OFF', or 'exit'.")
  
  time.sleep(1)
