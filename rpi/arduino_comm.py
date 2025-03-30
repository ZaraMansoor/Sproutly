#!/usr/bin/env python3
import serial

if __name__ == '__main__':
  ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
  time.sleep(2)
  ser.reset_input_buffer()

  while True:
    if ser.in_waiting > 0:
      line = ser.readline().decode('utf-8').strip()
      print(line)