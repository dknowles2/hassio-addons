#!/usr/bin/python3

import json
import optparse
import paho.mqtt.client as mqtt

parser = optparse.OptionParser()
parser.add_option('--mqtt_host', dest='mqtt_host', default='127.0.0.1')
parser.add_option('--mqtt_port', dest='mqtt_port', type='int', default=1883)
parser.add_option('--mqtt_user', dest='mqtt_user', default='genmon')
parser.add_option('--mqtt_pass', dest='mqtt_password', default='nomneg')
parser.add_option('--genmon_mqtt_root_topic', dest='genmon_mqtt_root_topic', default='')
parser.add_option('--genmon_url', dest='genmon_url', default='http://192.168.1.71:8000')
parser.add_option('--generator_device_name', dest='generator_device_name', default='Generator')
parser.add_option('--generator_manufacturer', dest='generator_manufacturer', default='Generac')
parser.add_option('--generator_model', dest='generator_model', default='Generic Generator')
parser.add_option('--generator_area', dest='generator_area', default='Backyard')


def engine(stat):
    return f'generator/Status/Engine/{stat}'


def line(stat):
    return f'generator/Status/Line/{stat}'


def log(log_type):
    return f'generator/Status/Last Log Entries/Logs/{log_type} Log'


def maintenance(stat):
    return f'generator/Maintenance/{stat}'


def outage(stat):
    return f'generator/Outage/{stat}'


def platform(stat):
    return f'generator/Monitor/Platform Stats/{stat}'


def power():
    return dict(
        device_class='power',
        unit_of_measurement='kW',
        value_template='{{ value | regex_replace(" *[Kk]W", "") | float | round(0) }}',
    )


def sanitize(s):
    return s.translate(s.maketrans(' /.', '___', '&'))


def voltage(precision=1):
    return dict(
        device_class='voltage',
        unit_of_measurement='V',
        value_template=f'{{{{ value | regex_replace(" V", "") | float | round({precision}) }}}}',
    )


class Discovery:

    def __init__(self, opts):
        self.opts = opts

    def publish(self, c):
        for topic, config in self._generate_sensors():
            config_json = json.dumps(config)
            c.publish(topic, config_json, False)

    def _generate_sensors(self):
        return [
            # Generator Sensors
            self.generator_sensor(
                line('Utility Voltage'), 'Utility Voltage', **voltage()),
            self.generator_sensor(
                engine('Battery Voltage'), 'Battery Voltage', **voltage()),
            self.generator_sensor(
                engine('RPM'), 'Engine RPM',
                unit_of_measurement='RPM',
                value_template='{{ value | int }}'),
            self.generator_sensor(
                engine('Frequency'), 'Engine Frequency',
                device_class='frequency',
                unit_of_measurement='Hz',
                value_template='{{ value | regex_replace(" Hz", "") | float }}'),
            self.generator_sensor(
                engine('Output Voltage'), 'Engine Output Voltage', **voltage()),
            self.generator_sensor(
                engine('Output Current'), 'Engine Output Current',
                device_class='current',
                unit_of_measurement='A',
                value_template='{{ value | regex_replace(" A", "") | float | round(1) }}'),
            self.generator_sensor(
                engine('Output Power (Single Phase)'),
                'Engine Output Power',
                **power()),
            self.generator_binary_sensor(
                outage('System in Outage'), 'Power Outage',
                payload_off='No',
                payload_on='Yes'),
            self.generator_sensor(log('Alarm'), 'Last Alarm Log', state_class='measurement'),
            self.generator_sensor(log('Service'), 'Last Service Log', state_class='measurement'),
            self.generator_sensor(log('Start Stop'), 'Last Action', state_class='measurement'),
            self.generator_sensor(
                maintenance('Rated kW'), 'Rated Capacity', **power()),
            self.generator_sensor(
                maintenance('Exercise/Exercise Time'), 'Exercise Time'),
            self.generator_sensor(
                maintenance('Service/Total Run Hours'), 'Total Run Time',
                device_class='duration',
                unit_of_measurement='h',
                value_template='{{ value | regex_replace(" +h$", "") | default(0) | float }}'),
            self.generator_sensor(
                maintenance('Service/Hardware Version'), 'Hardware Version'),
            self.generator_sensor(
                maintenance('Service/Firmware Version'), 'Firmware Version', state_class='measurement'),

            # Genmon Diagnostic Sensors
            self.genmon_sensor(
                platform('CPU Temperature'), 'CPU Temperature',
                device_class='temperature',
                unit_of_measurement='°F',
                value_template='{{ value | regex_replace(" F", "") | float | round(0) }}'),
            # TODO: Maybe parse this into raw hours?
            self.genmon_sensor(platform('System Uptime'), 'Uptime', state_class='measurement'),
            self.genmon_sensor(
                platform('CPU Utilization'), 'Load',
                unit_of_measurement='%',
                value_template='{{ value | regex_replace(" *%", "") | float | round(1) }}'),
            self.genmon_sensor(
                platform('WLAN Signal Level'), 'WLAN Signal Strength',
                device_class='signal_strength',
                unit_of_measurement='dBm',
                value_template='{{ value | regex_replace(" dBm", "") | float | round(1) }}'),
        ]

    def _sensor(self, component, state_topic, name, device, **kwargs):
        if self.opts.genmon_mqtt_root_topic:
            state_topic = self.opts.genmon_mqtt_root_topic.rstrip('/') + '/' + state_topic
        object_id = f'{sanitize(device["name"])}_{sanitize(name)}'.lower()
        config = {
            'platform': 'mqtt',
            'device': device,
            'enabled_by_default': True,
            'expire_after': 300,
            'force_update': True,
            'name': name,
            'object_id': object_id,
            'state_class': 'measurement',
            'state_topic': state_topic,
            'unique_id': object_id,
        }
        config.update(kwargs)
        discovery_topic = f'homeassistant/{component}/{config["unique_id"]}/config'
        return discovery_topic, config

    def generator_sensor(self, topic, name, **kwargs):
        return self._sensor('sensor', topic, name, self._generator(), **kwargs)

    def generator_binary_sensor(self, topic, name, **kwargs):
        return self._sensor(
            'binary_sensor', topic, name, self._generator(), **kwargs)

    def genmon_sensor(self, topic, name, **kwargs):
        return self._sensor('sensor', topic, name, self._genmon(), **kwargs)

    def _generator(self):
        return {
            'configuration_url': self.opts.genmon_url,
            'identifiers': ['generator_device'],
            'manufacturer': self.opts.generator_manufacturer,
            'model': self.opts.generator_model,
            'name': self.opts.generator_device_name,
            'suggested_area': self.opts.generator_area,
            'via_device': 'Genmon',
        }

    def _genmon(self):
        return {
            'configuration_url': self.opts.genmon_url,
            'identifiers': ['genmon_device'],
            'manufacturer': 'github.com/jgyates/genmon',
            'model': 'Genmon',
            'name': 'Genmon',
            'suggested_area': self.opts.generator_area,
        }


def main():
    opts, args = parser.parse_args()
    c = mqtt.Client()
    c.username_pw_set(opts.mqtt_user, opts.mqtt_password)
    c.connect(opts.mqtt_host, opts.mqtt_port, 60)
    d = Discovery(opts)
    try:
        d.publish(c)
    finally:
        c.disconnect()


if __name__ == '__main__':
    main()
