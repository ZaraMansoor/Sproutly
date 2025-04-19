# import RPi.GPIO as GPIO
# import time

# HUMIDIFIER_PIN_1 = 14
# HUMIDIFIER_PIN_2 = 21

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(HUMIDIFIER_PIN_1, GPIO.OUT)
# GPIO.setup(HUMIDIFIER_PIN_2, GPIO.OUT)

# def pulse_r_high():
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)

# def pulse_r_low():
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)

# def pulse_r():
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)
#     time.sleep(0.1)
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.LOW)

# def pulse_l_high():
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.HIGH)

# def pulse_l_low():
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.LOW)

# def pulse_l():
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.HIGH)
#     time.sleep(0.1)
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.LOW)

# def pulse():
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.HIGH)
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.HIGH)
#     time.sleep(0.1)
#     GPIO.output(HUMIDIFIER_PIN_1, GPIO.LOW)
#     GPIO.output(HUMIDIFIER_PIN_2, GPIO.LOW)

# while True:
#     try:
#         user_input = input("0 = all off; 1 = mister 1 on; 2 = mister 2 on; 3 = both misters on").strip().lower()

#         if user_input == '0':
#             pulse_l_high()
#             print("mister l is high")
#         elif user_input == '1':
#             pulse_l_low()
#             print("mister l is low")
#         elif user_input == '2':
#             pulse_r_high()
#             print("mister r is high")
#         elif user_input == '3':
#             pulse_r_low()
#             print("mister r is low")
#         elif user_input == 'exit':
#             print("Exiting program...")
#             break
#         else:
#             print("Invalid input. Please type 'ON', 'OFF', or 'exit'.")
    
#         time.sleep(1)

#     except KeyboardInterrupt:
#         GPIO.cleanup()

#     # time.sleep(2)
#     # while True:
#     #     print('turning on')
#     #     pulse_l()
#     #     time.sleep(5)
#     #     print('turning off')
#     #     pulse_l()
#     #     time.sleep(5)



from gpiozero import OutputDevice
import time

# Define the GPIO pins
HUMIDIFIER_PIN_1 = 14
HUMIDIFIER_PIN_2 = 21

# Create OutputDevice instances
mister_r = OutputDevice(HUMIDIFIER_PIN_1)
mister_l = OutputDevice(HUMIDIFIER_PIN_2)

def pulse(device):
    device.on()
    time.sleep(0.1)
    device.off()

while True:
    try:
        user_input = input("0 = all off; 1 = mister 1 on; 2 = mister 2 on; 3 = both misters on: ").strip().lower()

        if user_input == '0':
            mister_l.on()
            print("mister l is high (on)")
        elif user_input == '1':
            mister_l.off()
            print("mister l is low (off)")
        elif user_input == '2':
            mister_r.on()
            print("mister r is high (on)")
        elif user_input == '3':
            mister_r.off()
            print("mister r is low (off)")
        elif user_input == 'exit':
            print("Exiting program...")
            break
        else:
            print("Invalid input. Try 0, 1, 2, 3, or 'exit'.")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt. Exiting...")
        break
