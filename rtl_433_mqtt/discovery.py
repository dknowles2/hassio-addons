#!/usr/bin/python3

from __future__ import print_function
from __future__ import with_statement

import json
import optparse
import paho.mqtt.client as mqtt
import socket

parser = optparse.OptionParser()
parser.add_option("--host", action="store", dest="host", default="127.0.0.1")
parser.add_option("--port", action="store", dest="port", type="int", default=1883)
parser.add_option("--user", action="store", dest="user", default="rtl_433")
parser.add_option("--pass", action="store", dest="password", default="334_ltr")
parser.add_option(
    "--topic_host", action="store", dest="topic_host", default=socket.gethostname()
)

STATE_TOPIC_PREFIX_TEMPLATE = (
    "rtl_433/%(topic_host)s/devices/%(manufacturer_sanitized)s/%(sn)s"
)
DISCOVERY_TOPIC_TEMPLATE = "homeassistant/binary_sensor/%(unique_id)s/config"

KNOWN_DEVICES = {
    # 3720927 - entryway motion sensor
    ("DSC-Security", "DW4917 door/window sensor", "door"): {
        2959527: "Back Door",
        2898343: "Front Door",
        2651912: "Garage Door",
    },
    ("DSC-Security", "DW4917 door/window sensor", "window"): {
        2181141: "Basement Window Back",
        2885287: "Basement Window Side",
        2195683: "Kitchen Window",
        2176130: "Living Room Window 1",
        2295167: "Living Room Window 2",
        2237957: "Living Room Window 3",
        2347023: "Living Room Window 4",
        2965415: "Dining Room Window Front 1",
        2894503: "Dining Room Window Front 2",
        2402835: "Dining Room Window Side 1",
        2732723: "Dining Room Window Side 2",
        2179532: "Master Bedroom Window 1",
        2645436: "Master Bedroom Window 2",
        2630664: "Sitting Room Window 1",
        2865005: "Sitting Room Window 2",
    },
}

CONFIG_TEMPLATES = {
    "DSC-Security": {
        "DW4917 door/window sensor": [
            {
                "platform": "mqtt",
                "state_topic": STATE_TOPIC_PREFIX_TEMPLATE + "/closed",
                "device_class": "%(primary_device_class)s",
                "name": "%(device_name)s",
                "unique_id": "%(sn)s_%(primary_device_class)s",
                "payload_on": "0",
                "payload_off": "1",
                "device": {
                    "manufacturer": "%(manufacturer)s",
                    "model": "%(model)s",
                    "name": "%(device_name)s",
                    "identifiers": ["%(sn)s"],
                    "via_device": "rtl_433",
                },
            },
            {
                "platform": "mqtt",
                "state_topic": STATE_TOPIC_PREFIX_TEMPLATE + "/battery_ok",
                "device_class": "battery",
                "name": "%(device_name)s battery",
                "unique_id": "%(sn)s_battery",
                "payload_on": "0",
                "payload_off": "1",
                "device": {
                    "manufacturer": "%(manufacturer)s",
                    "model": "%(model)s",
                    "name": "%(device_name)s",
                    "identifiers": ["%(sn)s"],
                    "via_device": "rtl_433",
                },
            },
            {
                "platform": "mqtt",
                "state_topic": STATE_TOPIC_PREFIX_TEMPLATE + "/tamper",
                "device_class": "problem",
                "name": "%(device_name)s tamper",
                "unique_id": "%(sn)s_tamper",
                "payload_on": "1",
                "payload_off": "0",
                "device": {
                    "manufacturer": "%(manufacturer)s",
                    "model": "%(model)s",
                    "name": "%(device_name)s",
                    "identifiers": ["%(sn)s"],
                    "via_device": "rtl_433",
                },
            },
        ],
    },
}


def sanitize(name):
    return name.translate(name.maketrans(" /.", "___", "&"))


def get_sensors(topic_host):
    all_sensors = []
    for (manufacturer, model, primary_device_class), sn_name in KNOWN_DEVICES.items():
        for sn, name in sn_name.items():
            for tmpl in CONFIG_TEMPLATES[manufacturer][model]:
                sub = {
                    "manufacturer": manufacturer,
                    "manufacturer_sanitized": sanitize(manufacturer),
                    "model": model,
                    "model_sanitized": sanitize(model),
                    "primary_device_class": primary_device_class,
                    "sn": sn,
                    "device_name": name,
                    "device_id": sanitize(name),
                    "topic_host": topic_host,
                }
                dump = json.dumps(tmpl)
                config = json.loads(dump % sub)
                topic = DISCOVERY_TOPIC_TEMPLATE % config
                all_sensors.append((topic, config))
    return all_sensors


def publish_discovery(c, sensors):
    for topic, config in sensors:
        config_json = json.dumps(config)
        c.publish(topic, config_json, retain=True)


def main():
    opts, args = parser.parse_args()
    c = mqtt.Client()
    c.username_pw_set(opts.user, opts.password)
    c.connect(opts.host, opts.port, 60)
    try:
        publish_discovery(c, get_sensors(opts.topic_host))
    finally:
        c.disconnect()


if __name__ == "__main__":
    main()
