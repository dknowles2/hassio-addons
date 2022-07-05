# Genmon MQTT Discovery

This addon publishes MQTT discovery metadata for a Genmon instance, allowing
Home Assistant's MQTT integration to automatically discover a Genmon-monitored
generator and group all the sensors under appropriate devices.

This requires an install of [Genmon](https://github.com/jgyates/genmon) and to
have the "MQTT Integration" add-on enabled within Genmon.

Many thanks to the discussion thread in
https://community.home-assistant.io/t/monitor-your-generac-generator-with-home-assistant/62701
for inspiration here, and for supplying the initial manually-curated MQTT
topics.
