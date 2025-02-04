#include <EEPROM.h>
#include <DHT.h>

// Define the analog pin for the pH sensor
const int pHPin = A0; // Analog input pin
float voltage, pHValue;
float calibration = 2.5; // Calibration value for the pH sensor

#define DHT_PIN 2      // The pin to which the DHT sensor is connected
#define DHT_TYPE DHT11 // DHT sensor type (DHT22 or DHT11)
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600); // Start serial communication
  pinMode(pHPin, INPUT);
  dht.begin();        // Initialize the DHT sensor
}

void loop() {
  // Read the analog value from the pH sensor
  int sensorValue = analogRead(pHPin);

  // Convert the analog value to voltage (assuming 5V Arduino)
  voltage = sensorValue * (5.0 / 1023.0);

  // Convert the voltage to a pH value
  pHValue = 7 + ((2.5 - voltage) / calibration);

  // Read temperature and humidity from the DHT sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Send data to Serial Monitor
  if (!isnan(temperature) && !isnan(humidity)) {
    Serial.print("pH Value: ");
    Serial.print(pHValue);
    Serial.print(", Temperature: ");
    Serial.print(temperature);
    Serial.print(", Humidity: ");
    Serial.println(humidity);
  } else {
    Serial.println("Failed to read from the DHT sensor!");
  }

  // Delay for stability
  delay(2000);
}
