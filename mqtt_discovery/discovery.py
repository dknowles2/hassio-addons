"""Publishes Home Assistant MQTT discovery information."""

import json
import logging
import optparse
import sys
import threading
import time
from typing import Any

import paho.mqtt.client as mqtt
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

parser = optparse.OptionParser()
parser.add_option("--mqtt_host", dest="mqtt_host", default="192.168.1.11")
parser.add_option("--mqtt_port", dest="mqtt_port", type="int", default=1883)
parser.add_option("--mqtt_user", dest="mqtt_user", default="hass")
parser.add_option("--mqtt_pass", dest="mqtt_password", default="mosquitto")
parser.add_option("--publish_interval_secs", dest="publish_interval_secs", default=60)
parser.add_option("--config_file", dest="config_file", default="config.yaml")
parser.add_option("--dry_run", dest="dry_run", default=False)

DISCOVERY_TOPIC_TMPL = "homeassistant/%(component)s/%(object_id)s/config"
LOGGER = logging.getLogger("mqtt_discovery")
LOGGER.setLevel(logging.INFO)
logging.basicConfig(
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s",
)


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


class DiscoveryPublisher:
    def __init__(
        self,
        client: mqtt.Client,
        config_file: str,
        publish_interval_secs: int,
        dry_run: bool = False,
    ):
        self._client = client
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._config_file = config_file
        self._publish_interval_secs = publish_interval_secs
        self._dry_run = dry_run
        self._lock = threading.Lock()
        self._republish = {}  # protected by self._lock
        self._connected = False  # protected by self._lock
        self._initial_connect = threading.Event()

    def on_connect(self, client, userdata, flags, reason_code, *args, **kwargs):
        with self._lock:
            if reason_code != mqtt.CONNACK_ACCEPTED:
                LOGGER.error("Failed to connect: %s", mqtt.connack_string(reason_code))
                self._connected = False
            else:
                self._initial_connect.set()
                self._connected = True

    def loop(self):
        self._initial_connect.wait()
        LOGGER.debug("Starting loop")
        while self._connected:
            entities = self.read_config()
            self.publish(entities)
            time.sleep(self._publish_interval_secs)

    def read_config(self) -> list[tuple[str, str]]:
        with open(self._config_file) as f:
            config_yaml = yaml.load(f, Loader=Loader)
        LOGGER.debug("Read config.")
        try:
            self.refresh_republishers(config_yaml)
        except Exception as ex:
            LOGGER.error("Failed to refresh subscriptions: %s", ex)
        try:
            return parse(config_yaml)
        except Exception as ex:
            LOGGER.error("Failed to read entity config: %s", ex)
            return []

    def refresh_republishers(self, config_yaml: dict[Any, Any]):
        new_republishers = {}
        for republish in config_yaml.get("republish", []):
            if "topic" not in republish or "override" not in republish:
                LOGGER.error("Invalid republish: %s", republish)
                continue
            if republish["topic"] in new_republishers:
                LOGGER.warning("Duplicate republish topic: %s", republish["topic"])
            new_republishers[republish["topic"]] = republish["override"]

        with self._lock:
            old_topics = set(self._republish.keys())
            new_topics = set(new_republishers.keys())
            for topic in old_topics - new_topics:
                LOGGER.info("Unsubscribing from topic: %s", topic)
                self._client.unsubscribe(topic)
            for topic in new_topics - old_topics:
                LOGGER.info("Subscribing to topic: %s", topic)
                self._client.subscribe(topic)
            self._republish = new_republishers

    def publish(self, entities: list[tuple[str, str]]):
        """Publish discovery info for the given entities."""
        for topic, config_str in entities:
            if self._dry_run:
                LOGGER.info("DRY RUN: Would have published [%s] %s", topic, config_str)
            else:
                self._client.publish(topic, config_str, retain=True)

    def on_message(self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
        LOGGER.debug("Received message: [%s] %s", message.topic, message.payload)
        with self._lock:
            if message.topic not in self._republish:
                LOGGER.warning("Unknown topic: %s", message.topic)
                return
            new_payload = json.loads(message.payload)
            new_payload.update(self._republish[message.topic])
            new_payload_str = json.dumps(new_payload)
            old_payload_str = json.dumps(json.loads(message.payload))
            if old_payload_str == new_payload_str:
                # This is the message we just published. Don't publish it again.
                return
            if self._dry_run:
                LOGGER.info(
                    "DRY RUN: Would have published [%s] %s",
                    message.topic,
                    new_payload_str,
                )
            else:
                LOGGER.info("Republishing topic %s", message.topic)
                self._client.publish(message.topic, new_payload_str)


def main():
    opts, args = parser.parse_args()
    client = mqtt.Client(client_id="mqtt_discovery")
    publisher = DiscoveryPublisher(
        client, opts.config_file, opts.publish_interval_secs, opts.dry_run
    )
    try:
        client.username_pw_set(opts.mqtt_user, opts.mqtt_password)
        client.connect(opts.mqtt_host, opts.mqtt_port, 60)
        client.loop_start()
        publisher.loop()
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
