import serial
import requests


arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)


THINGSPEAK_API_KEY = 'YOUR_API_KEY'  
THINGSPEAK_URL = 'https://api.thingspeak.com/update'

while True:
    try:
        # Read data from Arduino
        line = arduino.readline().decode('utf-8').strip()
        if line:
            print(f"Received: {line}")
            # Parse the values
            data = line.split(',')
            if len(data) == 3:
                pH = float(data[0].split(':')[-1])
                temperature = float(data[1].split(':')[-1])
                humidity = float(data[2].split(':')[-1])

                # Send data to ThingSpeak
                response = requests.post(
                    THINGSPEAK_URL,
                    data={
                        'api_key': THINGSPEAK_API_KEY,
                        'field1': pH,
                        'field2': temperature,
                        'field3': humidity
                    }
                )
                print(f"ThingSpeak Response: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")
