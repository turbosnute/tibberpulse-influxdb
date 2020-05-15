# Pull base image
FROM ubuntu:latest

# Labels
LABEL MAINTAINER="Øyvind Nilsen <oyvind.nilsen@gmail.com>"

# Setup external package-sources
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* 

# Run pip install
RUN pip3 install influxdb websocket-client python-dateutil

# Environment
ENV PYTHONIOENCODING=utf-8
ADD get.sh /
ADD pulse_monitor.py /
CMD ["/bin/bash","/get.sh"]
