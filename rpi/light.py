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

# using GPIO pin 18
light = Relay(18, active_high=False)

while True:
    light.on()
    print("LED ON")
    sleep(10)
    
    light.off()
    print("LED OFF")
    sleep(10)