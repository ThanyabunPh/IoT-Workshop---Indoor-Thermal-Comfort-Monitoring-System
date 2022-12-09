import esp
import sys
import utime as time
import machine
import dht

LEDPin = machine.Pin(32, machine.Pin.OUT)

for i in range(10):
  
  try:
      LEDPin.value(0)
      time.sleep(1)
      
      LEDPin.value(1)
      time.sleep(1)
      
  except OSError as e:
    print('Failed')
