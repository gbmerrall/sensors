This is code for my local sensors setup.  It consists of 3 components.

 **1. Sensors**  
 Code for ESP32/ESP8266 sensors. Right now just doing some temperature stuff but will expand. T
 he nano3 sensors come from [this repo](https://github.com/Frapais/NanoCell-C3/tree/main)

 **2. Server**  
 The server that the sensors send data to. Simple FastAPI app that receives some JSON.  
 The important thing is the 'sensors.json' file. The server will happily accept an empty mac address
 until you update the sensors.json and then it will start logging the location. It's up to you to manually update the database for the old entries with the new location.

 **3. Dashbaord**  
 The main reporting interface. Uses plotly/dash which I know nothing about so just vibe-coded the
 whole thing. More interesting stuff to follow there as it's definitely a v0.99
 