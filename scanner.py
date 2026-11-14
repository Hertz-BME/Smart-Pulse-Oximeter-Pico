import machine

i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

devices = i2c.scan()

if devices:
    print("Success! The sensor has been found. Its secret address is:", devices)
else:
    print("Error: Nothing found. Check the wiring.")