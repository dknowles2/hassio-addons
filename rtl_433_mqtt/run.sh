#!/usr/bin/env bashio

mqtt_host="$(bashio::services mqtt host)"
mqtt_port="$(bashio::services mqtt port)"
mqtt_user="$(bashio::services mqtt username)"
mqtt_pass="$(bashio::services mqtt password)"

while true; do
    bashio::log.info "Publishing discovery info..."
    ./discovery.py \
        --host=${mqtt_host} \
        --port=${mqtt_port} \
        --user=${mqtt_user} \
        --pass=${mqtt_pass}
    sleep 60
done &

pub_pid=$!

bashio::log.info "Runnning rtl_433..."
/usr/local/bin/rtl_433 \
    -F "mqtt://${mqtt_host}:${mqtt_port},user=${mqtt_user},pass=${mqtt_pass},retain=1" \
    -F json \
    -C si \
    -M newmode \
    -v | while read l
do
    bashio::log.info $l
done


kill $pub_pid
