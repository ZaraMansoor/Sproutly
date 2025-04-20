#!/usr/bin/env python3
import serial
import time

if __name__ == '__main__':
  # ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
  ser = serial.Serial('/dev/tty.usbmodem1201', 19200)
  time.sleep(2)
  ser.reset_input_buffer()

  is_light_on = True
  is_water_on = False
  is_heater_on = True
  plant_healthy = False

  state_data = f"{int(is_light_on)},{int(is_water_on)},{int(is_heater_on)},{int(plant_healthy)}"
  ser.write(state_data.encode('utf-8'))
  print("Sent:", state_data)

  while True:
    if ser.in_waiting > 0:
      line = ser.readline().decode('utf-8').strip()
      print(line)