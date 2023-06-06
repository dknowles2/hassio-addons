ARG BUILD_FROM=homeassistant/amd64-base-python:3.9-alpine3.16
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

COPY discovery.py /
COPY run.sh /

RUN \
    pip install \
        --no-cache-dir \
        --prefer-binary \
        paho-mqtt \
    && chmod a+x /run.sh

CMD ["/run.sh"]
