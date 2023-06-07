ARG BUILD_FROM=homeassistant/amd64-base-python:3.9-alpine3.16
FROM ${BUILD_FROM}

ENV LANG C.UTF-8
ENV PIP_ROOT_USER_ACTION=ignore

RUN apk add --no-cache python3 py3-paho-mqtt py3-yaml

COPY discovery.py /
COPY run.sh /

RUN chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]
