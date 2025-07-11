Code for NanoCell-C3. See https://github.com/Frapais/NanoCell-C3/

Normally this device is used inside Home Assistant / ESPHome but I've flashed it to micropython using the standard esptool process.

max17408.py has been converted to Python from C by an LLM

rsyslog.py from https://github.com/kfricke/micropython-usyslog. Making a template for syslogd is an exercise for the reader.

**Note:**  When wiring up the AHT20 sensor, you can connect the Vin pin to the 3.3v out.