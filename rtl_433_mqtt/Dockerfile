ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8
LABEL maintainer="dknowles2@gmail.com"
LABEL description="This image is used to start a script that will monitor for RF events on 433Mhz and send the data to an MQTT server"

#
# First install software packages needed to compile rtl_433 and to publish MQTT events
#
RUN apk add --no-cache -t build-deps alpine-sdk cmake git libusb-dev librtlsdr-dev && \
    mkdir /tmp/src && \
    cd /tmp/src/ && \
    git clone https://github.com/merbanan/rtl_433 && \
    cd rtl_433/ && \
    mkdir build && \
    cd build && \
    cmake ../ && \
    make && \
    make install && \
    apk del build-deps && \
    rm -r /tmp/src
RUN apk add --no-cache libusb librtlsdr mosquitto-clients jq
RUN apk add --no-cache python3 py3-paho-mqtt

COPY discovery.py /
COPY run.sh /

ENTRYPOINT ["/run.sh"]
