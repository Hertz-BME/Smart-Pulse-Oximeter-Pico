from machine import Pin, I2C
from time import sleep
from max30102 import MAX30102
import hrcalc # Import HR and SpO2 calculation algorithm

# 1. Initialize I2C communication and MAX30102 sensor
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
sensor = MAX30102(i2c=i2c)

if sensor.check_part_id():
    print("Connection successful! Initializing the sensor...")
    sensor.setup_sensor()
else:
    print("Error: Unable to connect to the sensor.")

# 2. Data buffers to store 100 raw sensor samples
ir_data = []
red_data = []

print("Place your finger very gently on the sensor and wait for 4 seconds...")

# 3. Main signal acquisition and filtering loop
hr_history = []
spo2_history = []
final_hr = []
count = 0

while count < 20:
    sensor.check()

    if sensor.available():
        # Fetch raw Red and IR optical readings
        red = sensor.pop_red_from_storage()
        ir = sensor.pop_ir_from_storage()

        # Append new readings to sample buffers
        red_data.append(red)
        ir_data.append(ir)

        # Maintain buffer size at 100 samples
        if len(ir_data) > 100:
            ir_data.pop(0)
            red_data.pop(0)

        # Process signal once 100 samples are collected
        if len(ir_data) == 100:
            # Extract HR, SpO2, and signal validity flags
            hr_valid, hr, spo2_valid, spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)

            for i in range(25):
                ir_data.pop(0)
                red_data.pop(0)

            # Process valid biomedical readings only
            if hr_valid and spo2_valid:
                # 1. Append valid readings to history lists
                hr_history.append(hr)
                spo2_history.append(spo2)

                # 2. Sliding window of 12 readings (discard settling noise)
                if len(hr_history) > 12:
                    hr_history.pop(0)
                    spo2_history.pop(0)
                    final_hr.pop(0)

                # 3. Apply Moving Average filter for signal smoothing
                smoothed_hr = sum(hr_history) / len(hr_history)
                smoothed_spo2 = sum(spo2_history) / len(spo2_history)

                final_hr.append(smoothed_hr)

                # 4. Print smoothed HR and SpO2 values
                print("Pulse:", int(smoothed_hr), "BPM | Oxygen:", int(smoothed_spo2), "%")
                count += 1
            elif ir < 10000:
                # Detect finger removal via low IR intensity threshold
                print("--- Please place your finger firmly ---")

print("\n")
# 5. Decision Tree Classifier & Motion Artifact Detection
spread = max(final_hr) - min(final_hr)

if spread > 15:
    print("Class: Unstable Reading (Motion Artifact)")
else:
    if smoothed_spo2 < 92:
        print("Class: Low Oxygen Alert")

    if smoothed_hr > 100:
        print("Class: High Heart Rate, ( Active / Stressed )")
        
    elif smoothed_hr >= 50 and smoothed_hr <= 60:
        print("Class: Relaxed / Athletic State")

    elif smoothed_hr < 50:
        print("Class: Low Heart Rate")
        
    elif smoothed_spo2 >= 92:
        print("Class: Normal & Healthy State")