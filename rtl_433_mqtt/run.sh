#!/usr/bin/env bashio

echo "[version $(bashio::addon.version)]"
echo "[host $(bashio::addon.hostname)]"
echo "[mqtt $(bashio::services mqtt)]"

mqtt_host="$(bashio::services mqtt host)"
mqtt_port="$(bashio::services mqtt port)"

mqtt_user="$(bashio::services mqtt user)"
mqtt_pass="$(bashio::services mqtt pass)"

# FIXME:
mqtt_user="rtl_433"
mqtt_pass="334_ltr"

while true; do
    echo "Publishing discovery info..."
    ./discovery.py \
        --host=${mqtt_host} \
        --port=${mqtt_port} \
        --user=${mqtt_user} \
        --pass=${mqtt_pass}
    sleep 60
done &

pub_pid=$!

echo "Runnning rtl_433..."
/usr/local/bin/rtl_433 \
    -F "mqtt://${mqtt_host}:${mqtt_port},user=${mqtt_user},pass=${mqtt_pass},retain=1" \
    -F json \
    -C si \
    -M newmode \
    -v

kill $pub_pid
