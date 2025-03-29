from pymodbus.client.serial import ModbusSerialClient

# Configure Modbus RTU client
client = ModbusSerialClient(
    method="rtu",
    port="/dev/ttyUSB0",
    baudrate=9600,
    stopbits=1,
    parity='N',
    bytesize=8,
    timeout=1
)

if client.connect():
    # Read registers (start=18, count=2)
    response = client.read_holding_registers(address=18, count=2, unit=1)
    
    if response.isError():
        print("Error reading sensor data")
    else:
        humidity = response.registers[0] / 10.0  # Convert to %RH
        temperature_raw = response.registers[1]
        
        # Convert temperature (handle negative values)
        if temperature_raw > 32767:
            temperature_raw -= 65536
        temperature = temperature_raw / 10.0  # Convert to °C
        
        print(f"Soil Humidity: {humidity:.1f}% RH")
        print(f"Soil Temperature: {temperature:.1f}°C")

    client.close()
else:
    print("Failed to connect to sensor")
