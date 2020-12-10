FROM circleci/openjdk:8

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-setuptools \
  python3-pip \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install wheel
RUN pip3 install launchable
