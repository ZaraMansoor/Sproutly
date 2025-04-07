from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    # port="/dev/tty.usbserial-BG00R07C",    # Serial port for mac
    port="/dev/ttyUSB0",                   # Serial port for rpi
    baudrate=9600,                         # Baudrate for communication
    bytesize=8,                            # Number of bits per byte
    parity="N",                            # No parity
    stopbits=1,                            # One stop bit
)

if client.connect():
    print("Connected to Modbus device")

    ph_response = client.read_holding_registers(address=0x06, count=1, slave=1)
    if not ph_response.isError():
        ph = ph_response.registers[0]
        print(f"Soil pH            : {ph / 100.0} pH")
    else:
        print("Error reading soil pH data.")

    temp_hum_response = client.read_holding_registers(address=0x12, count=2, slave=1)

    if not temp_hum_response.isError():
        temp_hum_regs = temp_hum_response.registers
        print(f"Soil Moisture      : {temp_hum_regs[0] / 10.0} %RH")
        print(f"Soil Temperature   : {temp_hum_regs[1] / 10.0} °C")
    else:
        print("Error reading soil temperature and humidity data.")

    conductivity_response = client.read_holding_registers(address=0x15, count=1, slave=1)

    if not conductivity_response.isError():
        conductivity_regs = conductivity_response.registers
        print(f"Soil Conductivity  : {conductivity_regs[0]} μS/cm")
    else:
        print("Error reading soil conductivity data.")

    npk_response = client.read_holding_registers(address=0x1e, count=3, slave=1)

    if not npk_response.isError():
        npk_regs = npk_response.registers
        print(f"Soil Nitrogen      : {npk_regs[0]} mg/kg")
        print(f"Soil Phosphorus    : {npk_regs[1]} mg/kg")
        print(f"Soil Potassium     : {npk_regs[2]} mg/kg")
    else:
        print("Error reading soil npk data.")

    client.close()
else:
    print("Failed to connect to Modbus device")
