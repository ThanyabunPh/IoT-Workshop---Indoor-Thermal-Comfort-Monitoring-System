import esp
import sys
import utime as time
import machine
import dht
import urequests
import ntptime

# set a specific date and time 

# Create a dht object that refers to the sensor data pin, in this case is PIN 15
SENSOR_PIN = 15 
sensor = dht.DHT22(machine.Pin(SENSOR_PIN))

LEDPin = machine.Pin(2, machine.Pin.OUT)

WiFi_SSID = "WIFI_SSID"
WiFi_PASS = "WIFI_PASS"
WRITE_API_KEY = "API_KEY"

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...', WiFi_SSID)
        sta_if.active(True)
        sta_if.connect(WiFi_SSID, WiFi_PASS)
        while not sta_if.isconnected():
            print('.', end = '')
            time.sleep(1)
            pass
    print()
    print('network config: {}'.format(sta_if.ifconfig()))
    print()

import network
import ssl
connect()

# Synchronize time using NTP server
ntptime.settime()

# Get the current time
year, month, mday, hour, minute, second, weekday, yearday = time.localtime()

# Set RTC
rtc = machine.RTC()
rtc.datetime((year, month, mday, 0, hour + 7, minute, second, 0))


while(True):
  
  try:
      LEDPin.value(0)
      
      sensor.measure()
      temp = sensor.temperature()
      hum = sensor.humidity()
      
      t = rtc.datetime()
      
      now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])
      
      thermalComfort = 'n/a'
      thermalEncoding = 0
      
      if (temp < 24.1 and temp > 18.0) and (hum > 80.0): 
        thermalComfort = 'Good'
        thermalEncoding = 3
      elif (temp > 24.1 or temp < 18.0): 
        LEDPin.value(1)
        thermalComfort = 'Too warm'
        thermalEncoding = 2
      elif (hum < 80.0): 
        LEDPin.value(1)
        thermalComfort = 'Dehydration'
        thermalEncoding = 1
      else: 
        LEDPin.value(1)
        thermalComfort = 'Require attention'
        thermalEncoding = 0
      
      print("Time: ",  now, ' - ', thermalComfort)
      print('Sensor Temperature: %3.1f C' %temp)
      print('Sensor Humidity: %3.1f %%' %hum)
      print('  ')
      
      payload = "field1="+str(temp)+"&field2="+str(hum)+"&field3="+str(thermalEncoding)
      
      try:
          print('Posting Data ...')
          response = urequests.post("https://api.thingspeak.com/update?api_key=" + WRITE_API_KEY + "&" + payload)
          response.close()
          print('Completed ...\n')
      except OSError as e:
          print('Publish failed ...', e)
          time.sleep(5)
          machine.reset()
                
      time.sleep(5)
      
  except OSError as e:
    print('Failed to read data from the DHT22 sensor.')
