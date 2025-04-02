from gpiozero import OutputDevice
import time

class Relay(OutputDevice):
    def __init__(self, pin, active_high=False):
        super().__init__(pin, active_high=active_high)

# using GPIO pin 12
mister = Relay(12, active_high=False)


def press_mister(press_count=1, delay_between=0.5):
    """Simulates pressing the mister button press_count times."""
    for _ in range(press_count):
        mister.on()  # Close relay (press button)
        time.sleep(0.2)  # Duration of button press
        mister.off()   # Release relay
        if _ < press_count - 1:
            time.sleep(delay_between)  # Wait before next press

while True:
    user_input = input("Enter number of presses (1-3): ")
    if user_input in ["1", "2", "3"]:
        press_mister(int(user_input))
    else:
        print("Invalid input. Enter 1, 2, or 3.")
