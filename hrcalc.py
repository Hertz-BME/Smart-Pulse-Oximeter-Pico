# hrcalc.py
# Simplified HR and SpO2 calculation algorithm for MicroPython

def calc_hr_and_spo2(ir_data, red_data):
    # Ensure sufficient data is collected (100 consecutive samples)
    if len(ir_data) < 100 or len(red_data) < 100:
        return False, 0, False, 0
        
    ir_mean = int(sum(ir_data) / len(ir_data))
    
    # Peak detection (heartbeats) in the IR optical signal
    peaks = []
    for i in range(1, len(ir_data) - 1):
        if ir_data[i] > ir_mean and ir_data[i] > ir_data[i-1] and ir_data[i] > ir_data[i+1]:
            peaks.append(i)
            
    # Calculate Heart Rate (BPM)
    hr = 0
    hr_valid = False
    if len(peaks) >= 2:
        time_intervals = []
        for i in range(1, len(peaks)):
            # Assuming a sampling interval of 0.04 seconds (25 Hz)
            time_intervals.append((peaks[i] - peaks[i-1]) * 0.04) 
        
        avg_interval = sum(time_intervals) / len(time_intervals)
        hr = int(60.0 / avg_interval)
        hr_valid = True if 40 <= hr <= 180 else False
        
    # Calculate blood oxygen saturation (SpO2) via AC/DC ratio
    spo2 = 0
    spo2_valid = False
    if hr_valid:
        ir_ac = max(ir_data) - min(ir_data)
        red_ac = max(red_data) - min(red_data)
        red_dc = sum(red_data) / len(red_data)
        ir_dc = ir_mean
        
        if red_dc > 0 and ir_dc > 0:
            ratio = (red_ac / red_dc) / (ir_ac / ir_dc)
            # Standard MAX30102 SpO2 calibration equation
            spo2 = int(-45.060 * (ratio * ratio) + 30.354 * ratio + 94.845)
            spo2_valid = True if 50 <= spo2 <= 100 else False
            
    return hr_valid, hr, spo2_valid, spo2