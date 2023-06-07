ARG BUILD_FROM=homeassistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

ENV LANG C.UTF-8
ENV PIP_ROOT_USER_ACTION=ignore

RUN apk add --no-cache gcc libc-dev python3-dev yaml-dev

RUN pip3 install --verbose --no-cache-dir -I paho-mqtt
RUN pip3 install --verbose --no-cache-dir -I pyyaml

COPY discovery.py /
COPY run.sh /

RUN chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]
