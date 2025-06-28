# main.py -- put your code here!
import network # type: ignore
import ntptime # type: ignore
import requests
import time

# custom libs
import rsyslog
import ahtx0


from machine import SoftI2C, Pin, DEEPSLEEP, deepsleep, RTC, reset_cause # type: ignore

#TODO: Resolve rsyslog extra fields

WIFI_SSID = "KINOY"
WIFI_PASSWORD = "fourwordsalluppercase"
SERVER_IP = "192.168.86.250"
TEMP_URL = f"http://{SERVER_IP}:5000/temperature"
POWER_URL = f"http://{SERVER_IP}:5000/powerstatus"
SLEEP_TIME = 1   # minutes
NTP_HOST = "1.nz.pool.ntp.org"

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

def connect_wifi():
    """Connects to the WiFi network."""
    sta_if.active(True)
    ap_if.active(False)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    # TODO: Add a counter and bail after X attempts
    while sta_if.ifconfig()[0] == '0.0.0.0':
        print("No IP. Sleeping for a mo")
        time.sleep(0.5)
    print(f'Got IP {sta_if.ifconfig()}')
    return True

def set_ntptime():
    # time setting
    ntptime.host = NTP_HOST
    ntptime.settime()
    # send RTC back
    return RTC()
    
def get_time() -> RTC:
    rtc = set_ntptime()
    # to convert to NZT add 43200 seconds (12 hours)
    localtime = time.time() # + 43200
    (year, month, mday, hour, minute, second, weekday, yearday)=time.localtime(localtime)
    # first 0 = week of year
    # second 0 = milisecond
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))

    # format the timestamp. everything needs to be 0 padded
    # format: 2024-07-18T02:44:22+00:00
    now = f"{year}-{month:02}-{mday:02}T{hour:02}:{minute:02}:{second:02}+00:00"
    return now

def send_data(url: str, data: dict) -> bool:
    try:
        response = requests.post(url,
                                 headers={"Content-Type": "application/json; charset=utf-8"},
                                 json=data)
        print(response.text)
        if response.status_code != 200:
            print(f"Error sending data: {response.status_code}")
            print(data)
        else:
            print(f"Data sent successfully to {url}")
        return True
    except Exception as e:
        print(f"Error sending data: {e}")
        return False
    
def get_and_send_temp_data(aht20):
    data = {
        'mac': wlan_mac,
        'temperature': round(aht20.temperature,2),
        'humidity': round(aht20.relative_humidity,2),
        'timestamp': now
    }
    send_data(TEMP_URL, data)
    
print(f"Wakeup cause: {reset_cause()}")

#TODO: If no net connection log to file. Once network back, process log file
if not sta_if.isconnected():
    print('Connecting to WiFi')
    # network setup
    # Should check for False and then log to file
    connect_wifi()

# get mac address
wlan_mac = sta_if.config('mac').hex(':')

# hello to server
s = rsyslog.UDPClient(ip='192.168.86.250')
s.info(f"Checking in from {wlan_mac}")

# time 
now = get_time()

# Create the sensor object using I2C
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

# temp and humidity
aht20 = ahtx0.AHT20(i2c)
get_and_send_temp_data(aht20)

# we also need a sleep period to allow us to interrupt at power on
print("Goiing to time.sleep()")
time.sleep(5)

print("Going to deepsleep")
rtc = RTC()
rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)
#rtc.alarm(rtc.ALARM0, SLEEP_TIME * 60 * 1000)  # millis 
rtc.alarm(rtc.ALARM0, 5000)  # millis 
deepsleep()
