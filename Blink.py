import esp
import sys
import utime as time
import machine
import dht

LEDGreen = machine.Pin(32, machine.Pin.OUT)
LEDRed = machine.Pin(33, machine.Pin.OUT)

for i in range(10):
  
  try:
      LEDGreen.value(0)
      LEDRed.value(0)
      
      time.sleep(1)
      LEDRed.value(1)
      
      time.sleep(1)
      LEDGreen.value(1)
      LEDRed.value(0)
      
      time.sleep(1)
      
  except OSError as e:
    print('Failed')
