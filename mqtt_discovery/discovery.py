#!/usr/bin/python3
"""Publishes Home Assistant MQTT discovery information."""

import json
import optparse
from typing import Any
import paho.mqtt.client as mqtt
import yaml

parser = optparse.OptionParser()
parser.add_option("--mqtt_host", dest="mqtt_host", default="192.168.1.11")
parser.add_option("--mqtt_port", dest="mqtt_port", type="int", default=1883)
parser.add_option("--mqtt_user", dest="mqtt_user", default="hass")
parser.add_option("--mqtt_pass", dest="mqtt_password", default="mosqitto")
parser.add_option("--config_file", dest="config_file", default="config.yaml")

DISCOVERY_TOPIC_TMPL = "homeassistant/%(component)s/%(object_id)s/config"


def _sanitize(name: str) -> str:
    return name.translate(name.maketrans(" /.", "___", "&")).lower()


def parse(config_yaml: dict[Any, Any]) -> list[tuple[str, str]]:
    """Parse a config and return (topic, discovery payload) tuples."""
    entities = []
    templates = config_yaml.get("templates", {})

    for entity in config_yaml.get("entities", []):
        for template_name in entity["templates"]:
            template = templates[template_name]
            params = template.get("params", {})
            params.update(entity.get("params", {}))
            for k, v in list(params.items()):
                params[f"sanitized_{k}"] = _sanitize(str(v))

            object_id = template["object_id"] % params
            params["object_id"] = object_id
            params["component"] = template["component"]

            topic = DISCOVERY_TOPIC_TMPL % params
            config_str = json.dumps(template["config"])
            config_str %= params
            entities.append((topic, config_str))

    return entities


def publish(client: mqtt.Client, entities: list[tuple[str, str]]):
    """Publish discovery info for the given entities."""
    for topic, config_str in entities:
        client.publish(topic, config_str, retain=True)


def main():
    opts, arts = parser.parse_args()
    client = mqtt.Client()
    client.username_pw_set(opts.mqtt_user, opts.mqtt_password)
    client.connect(opts.mqtt_host, opts.mqtt_port, 60)
    with open(") as f:
        config_yaml = yaml.load(f, Loader=yaml.CLoader)
    entities = parse(config_yaml)
    try:
        publish(client, entities)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
