'''
This is file to control the water pump from the RPi GPIO 18

Zara Mansoor (zmansoor)
'''
from gpiozero import OutputDevice
import time

class Relay(OutputDevice):
  def __init__(self, pin, active_high=False):
    super().__init__(pin, active_high=active_high)

# water pump
WATER_PUMP_RELAY_PIN = 18
water_pump_relay = Relay(WATER_PUMP_RELAY_PIN, active_high=False)
water_pump_relay.off()

NUTRIENTS_PUMP_RELAY_PIN = 24
nutrients_pump_relay = Relay(NUTRIENTS_PUMP_RELAY_PIN, active_high=False)
nutrients_pump_relay.off()


while True:
  user_input = input("0 = all off; 1 = water pump on; 2 = nutrients pump on; 3 = both pumps on").strip().lower()

  if user_input == '0':
    water_pump_relay.off()
    nutrients_pump_relay.off()
    print("all OFF")
  elif user_input == '1':
    water_pump_relay.on()
    nutrients_pump_relay.off()
    print("water pump is ON")
  elif user_input == '2':
    water_pump_relay.off()
    nutrients_pump_relay.on()
    print("nutrients pump is ON")
  elif user_input == '3':
    water_pump_relay.on()
    nutrients_pump_relay.on()
    print("all ON")
  elif user_input == 'exit':
    print("Exiting program...")
    break
  else:
    print("Invalid input. Please type 'ON', 'OFF', or 'exit'.")
  
  time.sleep(1)
