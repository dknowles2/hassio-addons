#!/usr/bin/env bashio

conf_directory="/config/mqtt_discovery"
conf_file="${conf_directory}/conf.yaml"

if bashio::services.available "mqtt" ; then
    host=$(bashio::services "mqtt" "host")
    password=$(bashio::services "mqtt" "password")
    port=$(bashio::services "mqtt" "port")
    username=$(bashio::services "mqtt" "username")
else
    bashio::log.info "The mqtt addon is not available."
    bashio::log.info "Manually update the output line in the configuration file with mqtt connection settings, and restart the addon."
    exit 1
fi

if [[ ! -d ${conf_directory} ]]; then
    mkdir -p ${conf_directory}
    touch ${conf_file}
fi

while true; do
    bashio::log.info "Publishing discovery info..."
    python3 \
        -u /discovery.py \
        --mqtt_host=${host} \
        --mqtt_port=${port} \
        --mqtt_user=${username} \
        --mqtt_pass=${password} \
        --config_file=${conf_file}

    sleep 60
done
