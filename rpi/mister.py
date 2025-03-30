import os
import time

USB_PORT_PATH = "/sys/bus/usb/devices/usb1/power/control"

def turn_on():
    with open(USB_PORT_PATH, "w") as f:
        f.write("on")
    print("Mister ON")

def turn_off():
    with open(USB_PORT_PATH, "w") as f:
        f.write("auto")
    print("Mister OFF")

turn_on()
time.sleep(10)
turn_off()
time.sleep(10)
