# David's Home Assistant Addons

## gdrive_sync

Watches a directory for new files and uploads them to gDrive.

Used for moving scanned documents from a SMB share into gDrive.

## rtl_433_mqtt

Monitors RF signals on 433mhz and publishes them to MQTT in a Home
Assistant-compatible manner.

Essentially a Docker wrapper around https://github.com/merbanan/rtl_433 with a
custom script that publishes HA discovery events to MQTT for my RF devices I
want monitored.
