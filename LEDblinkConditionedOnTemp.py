import utime as time
import machine
import dht
import network
import ntptime


# กำหนดชื่อและรหัสผ่านของ WiFi
WiFi_SSID = "WIFI_SSID"
WiFi_PASSWORD = "WIFI_PASS"


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


# สร้างออปเจ็กต์ RTC
rtc = machine.RTC()

# เชื่อมต่อกับ WiFi และตั้งค่าเวลาก่อนเริ่มการทำงาน
connect_to_wifi()
setting_time()

# วนลูปอ่านค่าอุณหภูมิและความชื้นจาก DHT22 เปรียบเสมือนคนที่คอยตรวจวัดอุณหภูมิและความชื้นทุกๆ 5 วินาที
while True:

    # TRY คือ การป้องกันการเกิดข้อผิดพลาดจากการทำงานของโปรแกรมหรือเซ็นเซอร์ ถ้าเกิดข้อผิดพลาดให้ทำงานในส่วนของ EXCEPT
    try:

        # ปิดไฟ LED ที่ใช้แสดงสถานะ ก่อนอ่านค่าจาก DHT22
        LED_SENSOR.value(0)

        # อ่านค่าอุณหภูมิและความชื้นจาก DHT22
        DHT_SENSOR.measure()
        temperature = DHT_SENSOR.temperature()
        humidity = DHT_SENSOR.humidity()


        # เช็คว่าอุณหภูมิอยู่ในช่วงที่กำหนดหรือไม่ ถ้าไม่อยู่ในช่วงที่กำหนดให้เปิดไฟ LED เพื่อแจ้งเตือน
        # เสมือนคนที่คอยตรวจวัดอุณหภูมิและความชื้น ถ้าอุณหภูมิไม่อยู่ในช่วงที่กำหนด ก็๋จะแจ้งเตือนแก่เกษตรกร
        if temperature < 23.0 or temperature > 27.0:
            LED_SENSOR.value(1)
        else:
            LED_SENSOR.value(0)

        # อ่านค่าเวลาจาก RTC
        t = rtc.datetime()

        # แปลงค่าเวลาให้อยู่ในรูปแบบที่เราต้องการ
        now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])

        # แสดงผลลัพธ์
        print("Time: ", now)
        print('Sensor Temperature: %3.1f C' % temperature)
        print('Sensor Humidity: %3.1f %%' % humidity)
        print('  ')

        # หยุดรอ 5 วินาที ก่อนที่จะอ่านค่าอุณหภูมิและความชื้นใหม่อีกครั้ง
        time.sleep(5)

    # ถ้าเกิดข้อผิดพลาดในการอ่านค่าจาก DHT22 ให้แสดงข้อความว่า "Failed to read data from the DHT22 sensor." และรีบูตบอร์ด
    except OSError as e:
        print('Failed to read data from the DHT22 sensor.')
        time.sleep(15)
        machine.reset()
