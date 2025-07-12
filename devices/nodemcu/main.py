import requests
import time
import os
import json
import machine
import network

# local modules
import ahtx0
import config

# These variables are initialized in boot.py and are globally available:
# i2c, rtc, wlan_mac
# The sta_if object is also available from boot.py
OFFLINE_LOG_FILE = "offline_data.json"

TEMP_URL = f"http://{config.SERVER_IP}:{config.SERVER_PORT}/temperature"
POWER_URL = f"http://{config.SERVER_IP}:{config.SERVER_PORT}/powerstatus"
CONNECTION_URL = f"http://{config.SERVER_IP}:{config.SERVER_PORT}/connection"

# This block is never executed but provides type hints for the linter
# to understand the global variables initialized in boot.py.
if False:
    i2c = machine.SoftI2C(scl=machine.Pin(3), sda=machine.Pin(2))
    rtc = machine.RTC()
    wlan_mac = "00:00:00:00:00:00"
    sta_if = network.WLAN(network.STA_IF)  # station interface


def log(message: str):
    """Prints a message with a timestamp."""
    try:
        # Get current time from RTC
        year, month, mday, hour, minute, second, _, _ = time.localtime()
        # Format timestamp
        timestamp = f"[{year}-{month:02}-{mday:02} {hour:02}:{minute:02}:{second:02}]"
        print(f"{timestamp} {message}")
    except Exception:
        # Fallback if time is not set
        print(f"[no timestamp] {message}")


def send_data(url: str, data: dict) -> bool:
    try:
        response = requests.post(
            url, headers={"Content-Type": "application/json; charset=utf-8"}, json=data, timeout=10
        )
        log(f"Response from {url}: {response.status_code}")
        if response.status_code != 200:
            log(f"Error sending to {url}. Error: {response.text}")
        else:
            log("Data sent successfully.")
        # In MicroPython, it's good practice to close responses to free up memory.
        response.close()
        return response.status_code == 200
    except Exception as e:
        log(f"Error sending data to {url}: {e}")
        return False


def save_data_offline(url: str, data: dict):
    """Saves a data payload and its destination URL to the offline log file."""
    record = {"url": url, "payload": data}
    try:
        with open(OFFLINE_LOG_FILE, "a") as f:
            f.write(json.dumps(record))
            f.write("\n")
        log(f"Data for {url} saved offline.")
    except Exception as e:
        log(f"Failed to save data offline: {e}")


def check_server_availability() -> bool:
    """Checks if the server is available by making a GET request."""
    log("Checking server availability...")
    try:
        response = requests.get(CONNECTION_URL, timeout=5)
        is_available = response.status_code == 200
        response.close()
        if is_available:
            log("Server is available.")
        else:
            log(f"Server check failed with status code: {response.status_code}")
        return is_available
    except Exception as e:
        log(f"Error checking server availability: {e}")
        return False


def process_offline_log():
    """Reads the offline log file and tries to send each stored record."""
    try:
        with open(OFFLINE_LOG_FILE, "r") as f:
            lines = f.readlines()
    except OSError:
        return  # Log file doesn't exist

    log(f"Found {len(lines)} records in offline log. Processing...")

    unsent_records = []
    send_failed = False

    for line in lines:
        if send_failed:
            unsent_records.append(line)
            continue

        try:
            record = json.loads(line)
            if send_data(record["url"], record["payload"]):
                log("Successfully sent offline record.")
            else:
                log("Failed to send offline record. Will retry later.")
                send_failed = True
                unsent_records.append(line)
        except (ValueError, KeyError) as e:
            log(f"Skipping corrupted record in log file: {e}")
            continue

    if unsent_records:
        log(f"Rewriting log file with {len(unsent_records)} unsent records.")
        with open(OFFLINE_LOG_FILE, "w") as f:
            f.writelines(unsent_records)
    else:
        log("All offline records sent. Deleting log file.")
        os.remove(OFFLINE_LOG_FILE)


def get_temp_data(aht20, timestamp) -> dict:
    """Gets temperature and humidity data."""
    return {
        "mac": wlan_mac,
        "temperature": round(aht20.temperature, 2),
        "humidity": round(aht20.relative_humidity, 2),
        "timestamp": timestamp,
    }

def get_formatted_timestamp() -> str:
    """
    Returns the current time as an ISO 8601 formatted string in UTC.
    e.g., '2024-07-28T10:30:00+00:00'
    """
    # The time is set via NTP in boot.py, so we can just use time.localtime()
    year, month, mday, hour, minute, second, _, _ = time.localtime()

    # format the timestamp. everything needs to be 0 padded
    return f"{year}-{month:02}-{mday:02}T{hour:02}:{minute:02}:{second:02}+00:00"


# --- Execution starts here ---

is_online = sta_if.isconnected()
server_is_available = False

if is_online:
    log("Device is online. Checking for server availability.")
    server_is_available = check_server_availability()
    if server_is_available:
        # If server is available, first try to send any stored data
        process_offline_log()
    else:
        log("Server is not available. Will log data locally.")
else:
    log("Device is offline. Skipping check for server and offline log processing.")


# Get a single timestamp for this batch of readings.
now = get_formatted_timestamp()

# Get sensor data
aht20 = ahtx0.AHT20(i2c)
temp_data = get_temp_data(aht20, now)

# Send or save the current data based on network status
if server_is_available:
    log("Sending current sensor readings...")
    # Send sequentially. If one fails, we still try the next.
    send_data(TEMP_URL, temp_data)
else:
    log("Saving current sensor readings to offline log.")
    save_data_offline(TEMP_URL, temp_data)

# we also need a sleep period to allow us to interrupt at power on
log(f"Entering deep sleep for {config.SLEEP_TIME_MINUTES} minutes...")

# A short delay to allow for interrupting the script before deep sleep, useful for development.
#time.sleep(30)
# On ESP8266, deepsleep takes an integer argument in microseconds.
# For deep sleep to work, GPIO16 (D0 on many boards) must be connected to the RST pin.
sleep_us = config.SLEEP_TIME_MINUTES * 60 * 1000000
#machine.deepsleep(sleep_us)
