#!/usr/bin/python3

from __future__ import print_function
from __future__ import with_statement

import json
import optparse
import paho.mqtt.client as mqtt

parser = optparse.OptionParser()
parser.add_option('--host', action='store', dest='host', default='127.0.0.1')
parser.add_option('--port', action='store', dest='port', type='int', default=1883)
parser.add_option('--user', action='store', dest='user', default='rtl_433')
parser.add_option('--pass', action='store', dest='password', default='334_ltr')

STATE_TOPIC_PREFIX_TEMPLATE = (
    'rtl_433/%(host)s/devices/%(manufacturer_sanitized)s/%(sn)s')
DISCOVERY_TOPIC_TEMPLATE = 'homeassistant/binary_sensor/%(unique_id)s/config'

KNOWN_DEVICES = {
    # 3720927 - entryway motion sensor
    ('DSC-Security', 'DW4917 door/window sensor', 'door'): {
        2651912: 'Garage Door',
        2898343: 'Front Door',
        2959527: 'Back Door',
    },
    ('DSC-Security', 'DW4917 door/window sensor', 'window'): {
        2176130: 'Living Room Window North 1',
        2195683: 'Kitchen Window',
        2237957: 'Living Room Window North 3',
        2295167: 'Living Room Window North 2',
        2347023: 'Living Room Window North 4',
        2402835: 'Dining Room Window West 1',
        2630664: 'Sitting Room Window 1',
        2732723: 'Dining Room Window West 2',
        2865005: 'Sitting Room Window 2',
        2894503: 'Dining Room Window South 2',
        2965415: 'Dining Room Window South 1',
        2181141: 'Basement Window South',
        2885287: 'Basement Window East',
        2645436: 'Master Bedroom Window South 2',
        2179532: 'Master Bedroom Window South 1',
    },
}

CONFIG_TEMPLATES = {
    'DSC-Security': {
        'DW4917 door/window sensor': [
            {
                'platform': 'mqtt',
                'state_topic': STATE_TOPIC_PREFIX_TEMPLATE + '/closed',
                'device_class': '%(primary_device_class)s',
                'name': '%(device_name)s',
                'unique_id': '%(device_id)s_%(primary_device_class)s',
                'payload_on': '1',
                'payload_off': '0',
                'device': {
                    'manufacturer': '%(manufacturer)s',
                    'model': '%(model)s',
                    'name': '%(device_name)s',
                    'identifiers': ['%(sn)s'],
                    'via_device': 'rtl_433',
                },
            },
            {
                'platform': 'mqtt',
                'state_topic': STATE_TOPIC_PREFIX_TEMPLATE + '/battery_ok',
                'device_class': 'battery',
                'name': '%(device_name)s (Battery)',
                'unique_id': '%(device_id)s_battery',
                'payload_on': '0',
                'payload_off': '1',
                'device': {
                    'manufacturer': '%(manufacturer)s',
                    'model': '%(model)s',
                    'name': '%(device_name)s',
                    'identifiers': ['%(sn)s'],
                    'via_device': 'rtl_433',
                },
            },
            {
                'platform': 'mqtt',
                'state_topic': STATE_TOPIC_PREFIX_TEMPLATE + '/tamper',
                'device_class': 'problem',
                'name': '%(device_name)s (Tamper)',
                'unique_id': '%(device_id)s_tamper',
                'payload_on': '1',
                'payload_off': '0',
                'device': {
                    'manufacturer': '%(manufacturer)s',
                    'model': '%(model)s',
                    'name': '%(device_name)s',
                    'identifiers': ['%(sn)s'],
                    'via_device': 'rtl_433',
                },
            },
        ],
    },
}


def sanitize(name):
    return name.translate(name.maketrans(' /.', '___', '&'))


def get_sensors():
    all_sensors = []
    for ((manufacturer, model, primary_device_class),
         sn_name) in KNOWN_DEVICES.items():
        for sn, name in sn_name.items():
            for tmpl in CONFIG_TEMPLATES[manufacturer][model]:
                sub = {
                    'manufacturer': manufacturer,
                    'manufacturer_sanitized': sanitize(manufacturer),
                    'model': model,
                    'model_sanitized': sanitize(model),
                    'primary_device_class': primary_device_class,
                    'sn': sn,
                    'device_name': name,
                    'device_id': sanitize(name),
                    'host': 'local-rtl-433-to-mqtt',
                }
                dump = json.dumps(tmpl)
                config = json.loads(dump % sub)
                topic = DISCOVERY_TOPIC_TEMPLATE % config
                all_sensors.append((topic, config))
    return all_sensors


def publish_discovery(c, sensors):
    for topic, config in sensors:
        config_json = json.dumps(config)
        c.publish(topic, config_json, False)


def main():
    opts, args = parser.parse_args()
    c = mqtt.Client()
    c.username_pw_set(opts.user, opts.password)
    c.connect(opts.host, opts.port, 60)
    try:
        publish_discovery(c, get_sensors())
    finally:
        c.disconnect()


if __name__ == '__main__':
    main()
