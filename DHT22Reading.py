import esp
import sys
import utime as time
import machine
import dht
import network
import ntptime

# Connect to Wi-Fi
ssid = 'WIFI_SSID'
password = "WIFI_PASS"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    pass

print("Connected to Wi-Fi")

# Synchronize time using NTP server
ntptime.settime()

# Get the current time
year, month, mday, hour, minute, second, weekday, yearday = time.localtime()

# Set RTC
rtc = machine.RTC()
rtc.datetime((year, month, mday, 0, hour + 7, minute, second, 0))

# Create a dht object that refers to the sensor data pin, in this case is PIN 15
SENSOR_PIN = 15 
sensor = dht.DHT22(machine.Pin(SENSOR_PIN))

for i in range(10):
  
  try:    
      sensor.measure()
      temp = sensor.temperature()
      hum = sensor.humidity()
      
      t = rtc.datetime()
      
      now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])
      
      print("Time: ",  now)
      print('Sensor Temperature: %3.1f C' %temp)
      print('Sensor Humidity: %3.1f %%' %hum)
      print('  ')
      
      time.sleep(5)
      
  except OSError as e:
    print('Failed to read data from the DHT22 sensor.')
