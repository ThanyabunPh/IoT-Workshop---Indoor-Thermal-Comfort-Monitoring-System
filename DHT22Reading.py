import utime as time
import machine
import dht

# Create a dht object that refers to the sensor data pin, in this case is PIN 15
SENSOR_PIN = 15
DHT_Sensor = dht.DHT22(machine.Pin(SENSOR_PIN))

while True:
    try:
        DHT_Sensor.measure()
        temperature = DHT_Sensor.temperature()
        humidity = DHT_Sensor.humidity()

        print(f'Sensor Temperature: {temperature:.2f} C')
        print(f'Sensor Humidity: {humidity:.2f}')
        print('  ')

        time.sleep(5)

    except OSError as e:
        print('Failed to read data from the DHT22 sensor.')
        time.sleep(15)
        machine.reset()
