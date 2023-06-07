ARG BUILD_FROM=homeassistant/amd64-base-python:3.9-alpine3.16
FROM ${BUILD_FROM}

ENV LANG C.UTF-8
ENV PIP_ROOT_USER_ACTION=ignore

COPY discovery.py /
COPY run.sh /

RUN pip install --no-cache-dir --prefer-binary paho-mqtt
RUN pip install --no-cache-dir --no-binary pyyaml pyyaml
RUN chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]
