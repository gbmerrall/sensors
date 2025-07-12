import network  # type: ignore
import ntptime  # type: ignore
import time

import machine

# local modules
import config

# --- Global objects ---
# It's good practice to define these at the top level.
# They will be available in main.py after boot.py runs.
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
rtc = machine.RTC()
i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)


def connect_wifi(max_attempts: int = 3) -> bool:
    """
    Connects to the WiFi network with exponential backoff.

    Args:
        max_attempts: The maximum number of connection attempts.

    Returns:
        True if connected, False otherwise.
    """
    if sta_if.isconnected():
        return True

    print("Connecting to WiFi...")
    sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    attempts = 0
    backoff_delay_s = 2
    while attempts < max_attempts and not sta_if.isconnected():
        print(f"Retry {attempts + 1}/{max_attempts}...")
        time.sleep(backoff_delay_s)
        backoff_delay_s *= 2  # Double the delay for the next attempt
        attempts += 1

    if sta_if.isconnected():
        print(f"Successfully connected. IP: {sta_if.ifconfig()[0]}")
        return True
    else:
        print("Failed to connect to WiFi after max attempts.")
        sta_if.disconnect()
        return False


def set_ntptime():
    """Sets the system time from an NTP server."""
    try:
        print("Synchronizing time with NTP server...")
        ntptime.host = config.NTP_HOST
        ntptime.settime()
        print(f"Time synchronized: {time.localtime()}")
        return True
    except Exception as e:
        print(f"Error synchronizing time: {e}")
        return False


# --- Execution starts here ---

# The wlan_mac is needed in main.py, so we get it here.
# The interface must be active to get the MAC address.
sta_if.active(True)
wlan_mac = sta_if.config("mac").hex(":")

# Determine if this is a fresh boot or a wake from sleep
reset_cause = machine.reset_cause()
is_cold_boot = reset_cause != machine.DEEPSLEEP_RESET

print(f"Reset cause: {reset_cause}")
if is_cold_boot:
    print("Regular boot (power-on or hard reset).")
else:
    print("Woke from deep sleep.")

# Attempt to connect to WiFi. Let main.py handle the outcome.
if not connect_wifi():
    print("Could not connect to WiFi. Will attempt to log data locally.")

# If we are here, WiFi might be connected.
# Only sync NTP on a cold boot and if connected to save time.
if is_cold_boot and sta_if.isconnected():
    print("Syncing time with NTP server...")
    if not set_ntptime():
        print("Failed to sync time. Sleeping for 1 minute.")
        machine.deepsleep(60 * 1000)  # in millis


# The script will now proceed to main.py
