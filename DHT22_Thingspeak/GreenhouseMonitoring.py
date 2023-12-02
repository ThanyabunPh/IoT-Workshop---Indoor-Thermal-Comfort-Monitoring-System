import utime as time
import machine
import dht
import urequests
import ntptime
import network

# กำหนดชื่อ รหัสผ่านและ Key ของ ThingSpeak
WiFi_SSID = "WIFI_SSID"
WiFi_PASSWORD = "WIFI_PASS"
WRITE_API_KEY = "API_KEY"

# กำหนดขาที่เชื่อมต่อกับ DHT22
DHT_PIN = 33
LED_PIN = 27

# สร้างออปเจ็กต์ DHT22 และ LED
DHT_SENSOR = dht.DHT22(machine.Pin(DHT_PIN))
LED_SENSOR = machine.Pin(LED_PIN, machine.Pin.OUT)


# ชุดคำสั่งสำหรับการเชื่อมต่อกับ WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WiFi_SSID, WiFi_PASSWORD)
        i = 0
        while not wlan.isconnected():
            i += 1
            print(f'attempting #{i}')
            time.sleep(0.5)
    print('Network config:', wlan.ifconfig())


# ชุดคำสั่งสำหรับการตั้งค่าเวลา
def setting_time():
    # ตั้งค่าเวลาจาก Cloud
    ntptime.settime()

    # รับค่าเวลาปัจจุบันจาก RTC
    year, month, mday, hour, minute, second, weekday, yearday = time.localtime()

    # ปรับเวลาให้เป็นเวลาในประเทศไทย (UTC+7)
    rtc.datetime((year, month, mday, 0, hour + 7, minute, second, 0))


# ฟังก์ชันสำหรับการกระพริบ LED
def blink_led(times, delay=0.5):
    for _ in range(times):
        LED_SENSOR.value(1)
        time.sleep(delay)
        LED_SENSOR.value(0)
        time.sleep(delay)


# สร้างออปเจ็กต์ RTC
rtc = machine.RTC()

# เชื่อมต่อกับ WiFi และตั้งค่าเวลาก่อนเริ่มการทำงาน
connect_to_wifi()
setting_time()

# วนลูปอ่านค่าอุณหภูมิและความชื้นจาก DHT22 เปรียบเสมือนคนที่คอยตรวจวัดอุณหภูมิและความชื้น
while (True):

    # TRY คือ การป้องกันการเกิดข้อผิดพลาดจากการทำงานของโปรแกรมหรือเซ็นเซอร์ ถ้าเกิดข้อผิดพลาดให้ทำงานในส่วนของ EXCEPT
    try:

        # ปิดไฟ LED ที่ใช้แสดงสถานะ ก่อนอ่านค่าจาก DHT22
        LED_SENSOR.value(0)

        # อ่านค่าอุณหภูมิและความชื้นจาก DHT22
        DHT_SENSOR.measure()
        temp = DHT_SENSOR.temperature()
        hum = DHT_SENSOR.humidity()

        # อ่านค่าเวลาจาก RTC
        t = rtc.datetime()

        # แปลงค่าเวลาให้อยู่ในรูปแบบที่เราต้องการ
        now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])

        # วิเคราะห์ค่าอุณหภูมิและความชื้น และกำหนดสถานะของ LED และสถานะของการวิเคราะห์
        thermalComfort = 'n/a'
        thermalEncoding = 0
        if (temp < 24.1 and temp > 18.0) and (hum > 80.0):
            thermalComfort = 'Good'  # ในเงื่อนไขนี้ ค่าอุณหภูมิและความชื้นอยู่ในเกณฑ์ที่ดี
            thermalEncoding = 0
        elif (temp > 24.1 or temp < 18.0):
            LED_SENSOR.value(1)  # แสดงไฟแจ้งเตือน
            thermalComfort = 'Too warm'  # ในเงื่อนไขนี้ ค่าอุณหภูมิอยู่ในเกณฑ์ที่ร้อนเกินไป
            thermalEncoding = 1
        elif (hum < 80.0):
            LED_SENSOR.value(1)  # แสดงไฟแจ้งเตือน
            thermalComfort = 'Dehydration'  # ในเงื่อนไขนี้ ค่าความชื้นอยู่ในเกณฑ์ที่มีความชื้นน้อยเกินไป
            thermalEncoding = 2
        else:
            blink_led(3, 0.3) # แสดงไฟแจ้งเตือนในรูปแบบการกระพริบ เพื่อแสดงว่าต้องการการดูแลอย่างใกล้ชิด
            thermalComfort = 'Require attention'  # ในเงื่อนไขนี้ ต้องการการดูแลอย่างใกล้ชิด
            thermalEncoding = 3

        # แสดงผลลัพธ์ที่ได้จากการวิเคราะห์
        print("Time: ", now, ' - ', thermalComfort)
        print('Sensor Temperature: %3.1f C' % temp)
        print('Sensor Humidity: %3.1f %%' % hum)
        print('  ')

        # สร้างก้อนของข้อมูลที่จะส่งไปยัง ThingSpeak
        # โดยก้อนข้อมูลนี้จะประกอบไปด้วย อุณหภูมิ ความชื้น และสถานะของการวิเคราะห์
        # ใน Field ที่ 1 และ 2 จะเป็นข้อมูลอุณหภูมิและความชื้น ส่วน Field ที่ 3 จะเป็นสถานะของการวิเคราะห์
        # Field นี้จะตรงกับ Field ที่เราได้กำหนดไว้ใน ThingSpeak
        payload = "field1=" + str(temp) + "&field2=" + str(hum) + "&field3=" + str(thermalEncoding)

        try:
            # ส่งข้อมูลไปยัง ThingSpeak
            print('Posting Data ...')
            response = urequests.post("https://api.thingspeak.com/update?api_key=" + WRITE_API_KEY + "&" + payload)
            response.close()
            print('DHT22_Thingspeak ...\n')
        except OSError as e:
            # กรณีที่เกิดข้อผิดพลาดในการส่งข้อมูล ให้รีเซ็ตบอร์ด
            print('Publish failed ...', e)
            time.sleep(5)
            machine.reset()

        time.sleep(5)

    # กรณีที่เกิดข้อผิดพลาดในการอ่านค่าจาก DHT22 ให้รีเซ็ตบอร์ด
    except OSError as e:
        print('Failed to read data from the DHT22 sensor.')
