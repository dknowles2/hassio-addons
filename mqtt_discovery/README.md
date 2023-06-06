# MQTT Discovery Publisher

This addon publishes MQTT discovery metadata configured via YAML.

## Configuration

Place a file in /config/mqtt_discovery/conf.yaml like the following:

```
templates:
  # Dictionary of discovery templates.
  # |component| and |object_id| are required fields.
  # |object_id| may take python string substitions that are taken
  # from params in entity definitions. (See below)
  my_template:
    component: sensor
    object_id: "my_%(sanitized_name)s"
    config:
      device:
        name: My Device
        manufacturer: SpaceCorp
        model: Sprocket
        identifiers: [my_device]
      name: "%(name)s"
      platform: mqtt
      state_class: measurement
      state_topic: "my_topic/path/%(identifier)s/my_device/sensor"
      unique_id: "%(object_id)s"
      object_id: "%(object_id)s"
      value_template: '{{ value | float | round(1) }}'

entities:
  # Entity metadata to publish for auto-discovery.
  #
  # Params are used for string substitution in template expansion.
  # Before being passed, sanitized copies of each param will also be created
  # and added to the params dict with "sanitized_" prefixes.
  # The |component| and |object_id| are also added automatically before
  # used for template expansion.
  - params:
      name: My Sensor
      identifier: 12345
    templates: [my_template]
```

For each entity, its referenced templates will be expanded using the entity's
params. The discovery topic will be generated based on the `component` and
`object_id`.
