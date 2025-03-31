'''
File to control LED grow lights via relay

Jana Armouti
jarmouti
'''

from gpiozero import OutputDevice
from time import sleep

class Relay(OutputDevice):
    def __init__(self, pin, active_high=False):
        super().__init__(pin, active_high=active_high)

# using GPIO pins 26 6 5
light_1 = Relay(26, active_high=False)
light_2 = Relay(6, active_high=False)
light_3 = Relay(5, active_high=False)
white_light = Relay(16, active_high=False)

while True:
    user_input = input("how many lights? (0, 1, 2, 3 or white) ").strip().lower()

    if user_input == '0':
        light_1.off()
        light_2.off()
        light_3.off()
        white_light.off()
        print("0 lights are on")
    elif user_input == '1':
        light_1.on()
        light_2.off()
        light_3.off()
        white_light.off()
        print("1 light is on")
    elif user_input == '2':
        light_1.on()
        light_2.on()
        light_3.off()
        white_light.off()
        print("2 lights are on")
    elif user_input == '3':
        light_1.on()
        light_2.on()
        light_3.on()
        white_light.off()
        print("3 lights are on")
    elif user_input == 'white':
        light_1.off()
        light_2.off()
        light_3.off()
        white_light.on()
        print("white light is on")
    elif user_input == 'exit':
        print("Exiting program...")
        break
    else:
        print("Invalid input. Please type '0', 1', '2', or '3'.")
  
    sleep(1)

