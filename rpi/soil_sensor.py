import minimalmodbus

# Configure the RS485 Modbus connection
sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # Adjust port and device address (default 0x01)
sensor.serial.baudrate = 9600
sensor.serial.bytesize = 8
sensor.serial.parity = minimalmodbus.serial.PARITY_NONE
sensor.serial.stopbits = 1
sensor.serial.timeout = 1  # 1 second timeout

def read_soil_data():
    try:
        ph = sensor.read_register(0x06, 2)  # Read PH (unit: 0.01 pH)
        moisture = sensor.read_register(0x12, 1)  # Read Moisture (unit: 0.1 %RH)
        temp = sensor.read_register(0x13, 1)  # Read Temperature (unit: 0.1°C)
        conductivity = sensor.read_register(0x15, 0)  # Read Conductivity (unit: µS/cm)
        nitrogen = sensor.read_register(0x1E, 0)  # Read Nitrogen (unit: mg/kg)
        phosphorus = sensor.read_register(0x1F, 0)  # Read Phosphorus (unit: mg/kg)
        potassium = sensor.read_register(0x20, 0)  # Read Potassium (unit: mg/kg)

        print(f"Soil Data:\n"
              f"PH: {ph / 100:.2f}\n"
              f"Moisture: {moisture / 10:.1f}%\n"
              f"Temperature: {temp / 10:.1f}°C\n"
              f"Conductivity: {conductivity} µS/cm\n"
              f"Nitrogen: {nitrogen} mg/kg\n"
              f"Phosphorus: {phosphorus} mg/kg\n"
              f"Potassium: {potassium} mg/kg")
    except Exception as e:
        print("Error reading sensor data:", e)

# Run the function
read_soil_data()
