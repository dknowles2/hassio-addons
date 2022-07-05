ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8
LABEL maintainer="dknowles2@gmail.com"
LABEL description="This image is used to start a script that will broadcast Home Assistant MQTT discovery messages for Genmon."

#
# First install software packages needed to compile rtl_433 and to publish MQTT events
#
RUN apk add --no-cache mosquitto-clients jq python3 py3-paho-mqtt

COPY discovery.py /
COPY run.sh /

ENTRYPOINT ["/run.sh"]
