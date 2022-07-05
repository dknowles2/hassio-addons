#!/usr/bin/env bashio

while true; do
    bashio::log.info "Publishing discovery info..."
    ./discovery.py \
        --mqtt_host="$(bashio::services mqtt host)" \
        --mqtt_port="$(bashio::services mqtt port)" \
        --mqtt_user="$(bashio::services mqtt username)" \
        --mqtt_pass="$(bashio::services mqtt password)" \
        --genmon_mqtt_root_topic="$(bashio::config 'mqtt_root_topic' '')" \
        --genmon_url="$(bashio::config 'genmon_url' '')" \
        --generator_device_name="$(bashio::config 'generator_device_name' '')" \
        --generator_manufacturer="$(bashio::config 'generator_manufacturer' '')" \
        --generator_model="$(bashio::config 'generator_model' '')" \
        --generator_area="$(bashio::config 'generator_area' '')"
    sleep 60
done
